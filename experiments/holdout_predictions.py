#!/usr/bin/env python3
"""Freeze the existing interval rule's predictions through a new limit."""

import argparse
import bisect
import csv
import hashlib
import json
from pathlib import Path
import random

from candidate_formula import lattice_points, saved_report
from excess_rule import local_correction, predictions


def predicted_rows(limit):
    points = lattice_points(limit)
    colours = {n: (a - b) % 3 for n, a, b in points}
    active, counts, rows = set(), [0, 0, 0], []
    previous = 0
    for index, (t, a, b) in enumerate(points, start=1):
        # The only new corner is {t/3, 2t/3, t}, and exists iff b>0.
        if b:
            for n in (t // 3, 2 * t // 3, t):
                if n not in active:
                    active.add(n)
                    counts[colours[n]] += 1
        m, minima, rules = predictions(t, counts)
        excess = int(rules["dyadic_interval_and_relevant_colour_minimal"])
        candidate = index - min(counts)
        g = candidate + excess
        # Check a feasible witness for every predicted size, not optimality.
        if excess:
            witness = set(local_correction(t, m)["corrected_cover"])
        else:
            witness = {n for n in active if colours[n] == minima[0]}
        domain = {n for n, _, _ in points[:index]}
        if len(witness) != index - g or any(
            not ({n, 2*n, 3*n} & witness) for n in domain if 3*n in domain
        ):
            raise AssertionError(f"prediction infeasible at {t}")
        rows.append({
            "t": t, "a": a, "b": b, "points": index,
            "c_0": counts[0], "c_1": counts[1], "c_2": counts[2],
            "g_cand": candidate, "predicted_E": excess, "m": m,
            "g_pred": g, "predicted_jump_delta": g - previous,
        })
        previous = g
    return rows


def selection_plan(rows, old_limit, limit, seed, random_count):
    cutoffs = [row["t"] for row in rows]
    new = {row["t"]: row for row in rows if row["t"] > old_limit}
    tags = {t: [] for t in new}
    for t, row in new.items():
        if row["predicted_E"]:
            tags[t].append("predicted_E1")
    m = 0
    while 24 * 2**m <= limit:
        for edge_name, edge in (("lower", 24 * 2**m), ("upper", 27 * 2**m)):
            if edge > limit:
                continue
            index = bisect.bisect_left(cutoffs, edge)
            for offset, location in ((-1, "below"), (0, "at"), (1, "above")):
                neighbour = index + offset
                if 0 <= neighbour < len(cutoffs) and cutoffs[neighbour] in new:
                    tags[cutoffs[neighbour]].append(f"m={m}:{edge_name}:{location}")
        m += 1
    if new:
        tags[max(new)].append("largest_requested_smooth_cutoff")
        tags[min(new)].append("first_new_cutoff")
    eligible = sorted(t for t in new if not tags[t])
    sampled = random.Random(seed).sample(eligible, min(random_count, len(eligible)))
    for t in sampled:
        tags[t].append("random_sample")
    # Larger excess windows first, then edges, random sample, and all others.
    def priority(t):
        labels = tags[t]
        if "predicted_E1" in labels:
            return 0, -new[t]["m"], -t
        if any(":" in label for label in labels):
            return 1, -new[t]["m"], -t
        if "largest_requested_smooth_cutoff" in labels:
            return 2, 0, -t
        if "random_sample" in labels:
            return 3, 0, t
        return 4, 0, t
    return [{"t": t, "tags": tags[t], "priority_group": priority(t)[0]}
            for t in sorted(new, key=priority)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=10**14)
    parser.add_argument("--old-exact", type=Path, default=Path("experiments/results.json"))
    parser.add_argument("--seed", type=int, default=16820261004)
    parser.add_argument("--random-count", type=int, default=25)
    parser.add_argument("--output", type=Path, default=Path("experiments/predicted-1e14.json"))
    args = parser.parse_args()
    old, _, old_source = saved_report(args.old_exact)
    rows = predicted_rows(args.limit)
    by_t = {row["t"]: row for row in rows}
    for known in old["rows"]:
        if known["t"] <= args.limit and by_t[known["t"]]["g_pred"] != known["g"]:
            raise AssertionError("prediction reconstruction disagrees with old results")
    plan = selection_plan(rows, old["rows"][-1]["t"], args.limit, args.seed, args.random_count)
    report = {
        "limit": args.limit, "rule_frozen_at_commit": "6ca0694",
        "rule_source_sha256": hashlib.sha256(Path("experiments/excess_rule.py").read_bytes()).hexdigest(),
        "rule": "g_pred=points-min(c_j)+[exists m>=0:24*2^m<=t<27*2^m and c_((m+2)%3)=min(c_j)]",
        "old_exact_source": old_source, "old_last_t": old["rows"][-1]["t"],
        "smooth_count": len(rows), "last_smooth_t": rows[-1]["t"],
        "predicted_g_at_limit": rows[-1]["g_pred"],
        "predicted_jump_count": sum(row["predicted_jump_delta"] == 1 for row in rows),
        "predicted_jumps": [row["t"] for row in rows if row["predicted_jump_delta"] == 1],
        "jump_delta_anomalies": [row for row in rows if row["predicted_jump_delta"] not in (0, 1)],
        "holdout_count": len(plan), "random_seed": args.seed,
        "random_sample": [item["t"] for item in plan if "random_sample" in item["tags"]],
        "selection_plan": plan, "rows": rows,
        "interpretation": "Predictions fixed before holdout exact queries; feasibility checks do not establish optimality.",
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    with args.output.with_suffix(".csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    args.output.with_name(args.output.stem + "-jumps.txt").write_text(
        "\n".join(map(str, report["predicted_jumps"])) + "\n"
    )
    print(json.dumps({key: report[key] for key in (
        "smooth_count", "last_smooth_t", "predicted_g_at_limit",
        "predicted_jump_count", "holdout_count", "random_seed", "jump_delta_anomalies")}, indent=2))


if __name__ == "__main__":
    main()
