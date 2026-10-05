#!/usr/bin/env python3
"""Check whether each proposed extra omission belongs to no optimum.

Reuse the complete two-query membership results through prefix 200.
At every later E=1 cutoff, make a fresh exact MaxSAT query requiring
each pair point. Existing optimal cover witnesses contain both omissions,
so the exclusion direction is already witnessed at the optimum.
"""

import argparse
import json
from pathlib import Path
import time

import z3

from candidate_formula import saved_report
from exact_g import CoverSolver


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exact", type=Path, default=Path("experiments/results.json"))
    parser.add_argument("--excess", type=Path, default=Path("experiments/excess-results.json"))
    parser.add_argument("--forcing", type=Path, default=Path("experiments/forced-results.json"))
    parser.add_argument("--output", type=Path, default=Path("experiments/excess-pairs.json"))
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--engine", choices=("rc2", "maxres"), default="rc2")
    args = parser.parse_args()
    exact, points, provenance = saved_report(args.exact)
    exact_by_t = {row["t"]: row for row in exact["rows"]}
    excess = json.loads(args.excess.read_text())
    if excess["exact_source"]["sha256"] != provenance["sha256"]:
        raise AssertionError("excess report uses different exact source")
    forcing = {row["t"]: row for row in json.loads(args.forcing.read_text())["rows"]}
    rows, fresh_queries, reused_queries = [], 0, 0
    with args.output.with_suffix(".partial.jsonl").open("w") as checkpoint:
        for detail in excess["details"]:
            t, g = detail["t"], detail["exact_g"]
            saved = exact_by_t[t]
            weights = [n for n, _, _ in points if n <= t]
            domain = set(weights)
            triples = [(n, 2*n, 3*n) for n in weights if 3*n in domain]
            if any(point["weight"] not in saved["cover"] for point in detail["extra_pair"]):
                raise AssertionError(f"saved optimum does not witness pair exclusion at {t}")
            pair_rows = []
            for point in detail["extra_pair"]:
                n = point["weight"]
                started = time.perf_counter()
                if t in forcing:
                    known = next(p for p in forcing[t]["points"] if p["weight"] == n)
                    if known["g_excluded"] != g:
                        raise AssertionError("pair exclusion does not preserve optimum")
                    required_g = known["g_required"]
                    source = "saved two-constraint membership classification"
                    witness = None
                    reused_queries += 1
                else:
                    problem = CoverSolver(weights, triples, args.timeout_ms, args.engine)
                    minimum, cover = problem.solve(required=n)
                    required_g = len(weights) - minimum
                    source = "fresh exact MaxSAT requirement query"
                    witness = {"minimum_cover_lower": minimum,
                               "minimum_cover_upper": minimum, "cover": sorted(cover)}
                    fresh_queries += 1
                if required_g > g:
                    raise AssertionError("required optimum exceeds unrestricted optimum")
                pair_rows.append({
                    **point, "g_excluded": g, "g_required": required_g,
                    "status": "none" if required_g < g else "flexible",
                    "source": source, "requirement_witness": witness,
                    "seconds": round(time.perf_counter() - started, 6),
                })
                print(f"t={t} pair_point={n} g={g} required_g={required_g} "
                      f"status={pair_rows[-1]['status']} seconds={pair_rows[-1]['seconds']}", flush=True)
            row = {"t": t, "exact_g": g, "pair": pair_rows}
            rows.append(row)
            checkpoint.write(json.dumps(row) + "\n")
            checkpoint.flush()
    report = {
        "exact_source": provenance, "engine": args.engine,
        "z3_version": z3.get_version_string(), "cutoffs": len(rows),
        "fresh_requirement_queries": fresh_queries,
        "reused_requirement_queries": reused_queries,
        "all_pair_points_none": all(p["status"] == "none" for row in rows for p in row["pair"]),
        "counterexamples": [{"t": row["t"], **p} for row in rows for p in row["pair"]
                            if p["status"] != "none"],
        "rows": rows,
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
