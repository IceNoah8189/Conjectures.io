#!/usr/bin/env python3
"""Exact membership in every/no optimum, using two MaxSAT queries per point.

The unrestricted optimum and both constrained optima are computed from
the corner clauses. Neither saved values nor the jump criterion is used
to select a solution or classify a point.
"""

import argparse
import csv
import json
from pathlib import Path
import time

import z3

from exact_g import CoverSolver, smooth_points


def first_points(count):
    limit = 1
    while len(points := smooth_points(limit)) < count:
        limit *= 2
    return points[:count]


def brute_classification(points):
    """Intersect/union ALL maximum sets, enumerating numerical subsets."""
    weights = [n for n, _, _ in points]
    positions = {n: i for i, n in enumerate(weights)}
    corners = [
        sum(1 << positions[v] for v in (n, 2*n, 3*n))
        for n in weights if 3*n in positions
    ]
    best, common, union, count = -1, 0, 0, 0
    for subset in range(1 << len(weights)):
        size = subset.bit_count()
        if size < best or any(subset & corner == corner for corner in corners):
            continue
        if size > best:
            best, common, union, count = size, subset, subset, 1
        else:
            common &= subset
            union |= subset
            count += 1
    return {
        "g": best,
        "forced": [n for i, n in enumerate(weights) if common & (1 << i)],
        "none": [n for i, n in enumerate(weights) if not union & (1 << i)],
        "optimal_set_count": count,
    }


def classify_prefix(points, timeout_ms, engine, brute_prefixes):
    started = time.perf_counter()
    weights = [n for n, _, _ in points]
    domain = set(weights)
    triples = [(n, 2*n, 3*n) for n in weights if 3*n in domain]
    problem = CoverSolver(weights, triples, timeout_ms, engine)
    minimum, cover = problem.solve()
    g = len(points) - minimum
    rows = []
    for n, a, b in points:
        query_started = time.perf_counter()
        excluded_minimum, _ = problem.solve(excluded=n)
        required_minimum, _ = problem.solve(required=n)
        g_excluded = len(points) - excluded_minimum
        g_required = len(points) - required_minimum
        if max(g_excluded, g_required) != g:
            raise AssertionError("constrained optima do not recover the optimum")
        if g_excluded not in (g, g - 1):
            raise AssertionError("exclusion violates the one-point bound")
        status = ("forced" if g_excluded < g else
                  "none" if g_required < g else "flexible")
        rows.append({
            "weight": n, "a": a, "b": b, "status": status,
            "g_excluded": g_excluded, "g_required": g_required,
            "seconds": round(time.perf_counter() - query_started, 6),
        })
    forced = [row["weight"] for row in rows if row["status"] == "forced"]
    none = [row["weight"] for row in rows if row["status"] == "none"]
    result = {
        "prefix": len(points), "t": weights[-1], "g": g,
        "minimum_cover_lower": minimum, "minimum_cover_upper": minimum,
        "cover": sorted(cover), "forced": forced, "none": none,
        "flexible_count": len(points) - len(forced) - len(none),
        "constrained_query_count": 2 * len(points), "points": rows,
    }
    if len(points) <= brute_prefixes:
        oracle = brute_classification(points)
        if (oracle["g"], oracle["forced"], oracle["none"]) != (g, forced, none):
            raise AssertionError(f"exhaustive disagreement at prefix {len(points)}")
        result["brute_force"] = oracle
    result["seconds"] = round(time.perf_counter() - started, 6)
    return result


def jump_check(previous, current):
    """Evaluate the criterion on the PREVIOUS prefix, after solving."""
    new = current["points"][-1]
    current["jump"] = current["g"] - (previous["g"] if previous else 0)
    if current["jump"] not in (0, 1):
        raise AssertionError("g violates the one-point bound")
    if new["b"] == 0:
        current["jump_test"] = {
            "type": "power_of_two", "predicted_jump": True,
            "matches": current["jump"] == 1,
        }
    else:
        lower_weights = (new["weight"] // 3, 2 * new["weight"] // 3)
        by_weight = {row["weight"]: row for row in previous["points"]}
        statuses = [by_weight[n]["status"] for n in lower_weights]
        predicted = any(status != "forced" for status in statuses)
        current["jump_test"] = {
            "type": "previous_optimum_omits_lower_neighbor",
            "previous_prefix": previous["prefix"],
            "lower_weights": list(lower_weights),
            "previous_statuses": statuses,
            "predicted_jump": predicted,
            "matches": bool(current["jump"]) == predicted,
        }
    current["new_point_forced_iff_jump"] = (
        (new["status"] == "forced") == bool(current["jump"])
    )


def make_report(rows, engine, brute_prefixes, comparison_path):
    comparison = None
    if comparison_path:
        known = {
            row["t"]: row["g"]
            for row in json.loads(comparison_path.read_text())["rows"]
        }
        disagreements = [
            {"t": row["t"], "computed": row["g"], "saved": known.get(row["t"])}
            for row in rows if known.get(row["t"]) != row["g"]
        ]
        comparison = {"path": str(comparison_path), "disagreements": disagreements}
        if disagreements:
            raise AssertionError(f"saved optimum disagreement: {disagreements}")
    return {
        "method": "Boolean corner hitting-set MaxSAT; two constrained optima per point",
        "engine": engine, "z3_version": z3.get_version_string(),
        "prefix_count": len(rows), "last_t": rows[-1]["t"],
        "point_classifications": sum(row["prefix"] for row in rows),
        "constrained_queries": sum(row["constrained_query_count"] for row in rows),
        "unrestricted_queries": len(rows),
        "brute_force_prefixes": min(brute_prefixes, len(rows)),
        "comparison": comparison,
        "jump_criterion_cases": sum(row["jump_test"]["type"] != "power_of_two"
                                    for row in rows),
        "jump_criterion_disagreements": [row["t"] for row in rows
                                         if not row["jump_test"]["matches"]],
        "new_point_forced_iff_jump_disagreements": [row["t"] for row in rows
                                                    if not row["new_point_forced_iff_jump"]],
        "total_seconds": round(sum(row["seconds"] for row in rows), 6),
        "rows": rows,
    }


def write_table(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "prefix", "t", "g", "jump", "weight", "a", "b", "status",
            "g_excluded", "g_required", "exclusion_loss", "requirement_loss",
        ])
        writer.writeheader()
        for prefix in rows:
            for point in prefix["points"]:
                writer.writerow({
                    "prefix": prefix["prefix"], "t": prefix["t"],
                    "g": prefix["g"], "jump": prefix["jump"],
                    **{key: point[key] for key in
                       ("weight", "a", "b", "status", "g_excluded", "g_required")},
                    "exclusion_loss": prefix["g"] - point["g_excluded"],
                    "requirement_loss": prefix["g"] - point["g_required"],
                })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefixes", type=int, default=200)
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--engine", choices=("rc2", "maxres"), default="rc2")
    parser.add_argument("--brute-prefixes", type=int, default=16)
    parser.add_argument("--compare", type=Path)
    parser.add_argument("--output", type=Path, default=Path("experiments/forced-results.json"))
    args = parser.parse_args()
    if args.prefixes < 1 or not 0 <= args.brute_prefixes <= 22:
        parser.error("positive prefix count and brute-prefixes between 0 and 22 required")
    points = first_points(args.prefixes)
    rows = []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.with_suffix(".partial.jsonl").open("w") as checkpoint:
        for count in range(1, args.prefixes + 1):
            row = classify_prefix(points[:count], args.timeout_ms, args.engine,
                                  args.brute_prefixes)
            jump_check(rows[-1] if rows else None, row)
            rows.append(row)
            checkpoint.write(json.dumps(row) + "\n")
            checkpoint.flush()
            if count % 5 == 0 or row["seconds"] > 1:
                print(f"prefix={count} t={row['t']} g={row['g']} "
                      f"forced={len(row['forced'])} none={len(row['none'])} "
                      f"seconds={row['seconds']}", flush=True)
    report = make_report(rows, args.engine, args.brute_prefixes, args.compare)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    write_table(args.output.with_suffix(".csv"), rows)
    print(json.dumps({key: value for key, value in report.items() if key != "rows"},
                     indent=2), flush=True)
    if report["jump_criterion_disagreements"]:
        raise SystemExit("jump criterion disagrees with computed optima")


if __name__ == "__main__":
    main()
