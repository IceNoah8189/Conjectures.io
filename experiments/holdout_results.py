#!/usr/bin/env python3
"""Recheck saved holdout witnesses and compare them with frozen predictions.

This uses only the standard library and never calls an optimization solver.
The original 507-prefix fitting sample is kept separate and unchanged.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path

from candidate_formula import compare, lattice_points, saved_report


def provenance(path):
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def read_solver(path):
    if path.suffix == ".jsonl":
        rows = [json.loads(line) for line in path.read_text().splitlines() if line]
        report = {"rows": rows, "checkpoint_only": True}
    else:
        report = json.loads(path.read_text())
        rows = report["rows"]
    if len({r["t"] for r in rows}) != len(rows):
        raise AssertionError(f"duplicate cutoff in {path}")
    exact = [row for row in rows if row["status"] == "exact"]
    return report, rows, {
        **provenance(path), "attempted": len(rows), "exact": len(exact),
        "not_exact": len(rows)-len(exact),
        "peak_worker_rss_kib": max((r.get("proc_peak_rss_kib", 0) for r in rows), default=0),
        "slowest_query_seconds": max((r["wall_seconds"] for r in rows), default=0),
        "sum_query_wall_seconds": round(sum(r["wall_seconds"] for r in rows), 6),
        "checkpoint_only": report.get("checkpoint_only", False),
    }


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows({k: "|".join(v) if isinstance(v, list) else v for k, v in row.items()}
                         for row in rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, default=Path("experiments/predicted-1e14.json"))
    parser.add_argument("--old-exact", type=Path, default=Path("experiments/results.json"))
    parser.add_argument("--solver-reports", nargs="+", type=Path,
                        default=[Path("experiments/holdout-z3.json"), Path("experiments/holdout-cpsat.json"),
                                 Path("experiments/holdout-cpsat-retry.json"),
                                 Path("experiments/holdout-cpsat-retry-large.json")])
    parser.add_argument("--output", type=Path, default=Path("experiments/holdout-results.json"))
    parser.add_argument("--combined-exact", type=Path, default=Path("experiments/results-1e14.json"))
    args = parser.parse_args()
    prediction = json.loads(args.predictions.read_text())
    old, _, old_source = saved_report(args.old_exact)
    if old_source["sha256"] != prediction["old_exact_source"]["sha256"]:
        raise AssertionError("original fitting sample changed after prediction freeze")
    rule_hash = hashlib.sha256(Path("experiments/excess_rule.py").read_bytes()).hexdigest()
    if rule_hash != prediction["rule_source_sha256"]:
        raise AssertionError("rule changed after prediction freeze")
    planned = {row["t"]: row for row in prediction["selection_plan"]}
    predicted = {row["t"]: row for row in prediction["rows"]}
    points = lattice_points(prediction["limit"])
    if points != [(r["t"], r["a"], r["b"]) for r in prediction["rows"]]:
        raise AssertionError("frozen predicted domain is not the complete smooth lattice")
    known = {row["t"]: {**row, "solver_backend": "original saved MaxSAT"} for row in old["rows"]}
    exact_sources, attempts, sources = {}, {}, []
    for path in args.solver_reports:
        _, rows, source = read_solver(path)
        sources.append(source)
        for row in rows:
            t = row["t"]
            if t not in planned:
                raise AssertionError(f"query outside frozen holdout plan: {t}")
            if row["g_pred"] != predicted[t]["g_pred"]:
                raise AssertionError(f"post-query prediction changed at {t}")
            engine = row.get("engine", source["path"])
            attempts.setdefault(t, []).append(row)
            if row["status"] != "exact":
                continue
            weights = {n for n, _, _ in points if n <= t}
            h = len(weights)-row["g"]
            cover = set(row["cover"])
            if (row["points"], row["minimum_cover_lower"], row["minimum_cover_upper"]) != (len(weights), h, h):
                raise AssertionError(f"inconsistent saved exact bounds at {t}")
            if (len(cover) != h or len(row["cover"]) != h or not cover <= weights
                    or any(not ({n, 2*n, 3*n} & cover) for n in weights if 3*n in weights)):
                raise AssertionError(f"invalid saved exact witness at {t}")
            if t in known and row["g"] != known[t]["g"]:
                raise AssertionError(f"exact solver disagreement at {t}")
            exact_sources.setdefault(t, []).append(engine)
            known[t] = {
                key: row[key] for key in ("t", "points", "g", "cover",
                                         "minimum_cover_lower", "minimum_cover_upper", "seconds")
            }
            known[t]["solver_backend"] = engine
    missing = sorted(set(planned)-set(known))
    if missing:
        raise RuntimeError(f"{len(missing)} cutoffs still need exact answers: {missing}")

    # Validate the complete domain, not just one solver's successful subset.
    exact_rows = [known[t] for t in sorted(predicted)]
    previous = 0
    for row in exact_rows:
        row["jump"] = row["g"]-previous
        previous = row["g"]
    combined = {"limit": prediction["limit"], "smooth_count": len(exact_rows),
                "original_fitting_sample": old_source, "holdout_sources": sources,
                "rows": exact_rows,
                "interpretation": "Closed unrestricted solver optima with checked witnesses; not Lean proofs."}
    # compare() reconstructs all coordinate corners, numerical corners,
    # participation counts, bounds, covers and increments independently.
    comparison = compare(combined, points)
    for row in comparison:
        expected = predicted[row["t"]]
        for key in ("points", "g_cand", "c_0", "c_1", "c_2"):
            if row[key] != expected[key]:
                raise AssertionError(f"independent {key} reconstruction disagrees at {row['t']}")
    combined["jumps"] = [row["t"] for row in exact_rows if row["jump"]]
    combined["jump_count"] = len(combined["jumps"])
    combined["last_smooth_t"] = exact_rows[-1]["t"]

    rows = []
    by_t = {r["t"]: r for r in comparison}
    for t in sorted(planned):
        p, actual = predicted[t], known[t]
        rows.append({
            "t": t, "a": p["a"], "b": p["b"], "points": p["points"],
            "c_0": p["c_0"], "c_1": p["c_1"], "c_2": p["c_2"],
            "g_cand": p["g_cand"], "predicted_E": p["predicted_E"], "m": p["m"],
            "g_pred": p["g_pred"], "exact_g": actual["g"],
            "exact_E": by_t[t]["difference"], "difference": actual["g"]-p["g_pred"],
            "predicted_jump": p["predicted_jump_delta"], "exact_jump": actual["jump"],
            "exact_sources": sorted(set(exact_sources[t])), "tags": planned[t]["tags"],
        })
    mismatches = [row for row in rows if row["difference"]]
    joint = [t for t, engines in exact_sources.items() if "rc2" in engines and "cp_sat" in engines]
    coverage = {}
    for label, test in (
        ("predicted_E1", lambda tags: "predicted_E1" in tags),
        ("window_edge_neighbours", lambda tags: any(":" in tag for tag in tags)),
        ("random_sample", lambda tags: "random_sample" in tags),
    ):
        selected = [t for t, item in planned.items() if test(item["tags"])]
        coverage[label] = {"selected": len(selected), "exact": len(selected),
                           "mismatches": [row["t"] for row in mismatches if row["t"] in selected]}
    report = {
        "predictions_source": provenance(args.predictions), "old_exact_source": old_source,
        "solver_sources": sources, "rule_frozen_at_commit": prediction["rule_frozen_at_commit"],
        "rule_source_sha256": rule_hash,
        "new_cutoffs": len(rows), "new_exact_cutoffs": len(rows),
        "total_verified_cutoffs": len(exact_rows), "largest_verified_cutoff": exact_rows[-1]["t"],
        "exact_g_at_limit": exact_rows[-1]["g"], "predicted_jump_count": prediction["predicted_jump_count"],
        "verified_jump_count": len(combined["jumps"]),
        "predicted_and_exact_jump_sets_equal": combined["jumps"] == prediction["predicted_jumps"],
        "cross_solver_matching_exact_cutoffs": len(joint), "cross_solver_cutoffs": sorted(joint),
        "difference_convention": "exact_g - g_pred",
        "priority_coverage": coverage, "mismatches": mismatches, "unverified_cutoffs": [],
        "new_excess_cutoffs": [r["t"] for r in rows if r["exact_E"]], "rows": rows,
        "verification": "Every coordinate/numerical corner, colour count, optimum bound and cover rechecked; no solver was rerun by this program; no Lean proof.",
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    write_csv(args.output.with_suffix(".csv"), rows)
    args.combined_exact.write_text(json.dumps(combined, indent=2) + "\n")
    full_table = [{**r, "g_pred": predicted[r["t"]]["g_pred"],
                   "prediction_difference": r["exact_g"]-predicted[r["t"]]["g_pred"]} for r in comparison]
    write_csv(args.combined_exact.with_suffix(".csv"), full_table)
    args.output.with_name("verified-1e14-jumps.txt").write_text(
        "\n".join(map(str, combined["jumps"])) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in (
        "rows", "cross_solver_cutoffs", "verification")}, indent=2))


if __name__ == "__main__":
    main()
