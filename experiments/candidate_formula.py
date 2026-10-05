#!/usr/bin/env python3
"""Compare the participating-colour candidate with saved exact optima.

This uses only Python's standard library. It reconstructs every lattice
prefix and its corners, verifies feasible colour-class covers, and checks
saved exact objective bounds and witnesses. It does not rerun MaxSAT.
"""

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path


FIELDS = ("t", "exact_g", "g_cand", "difference", "points", "c_0", "c_1", "c_2")


def lattice_points(limit):
    result = []
    power3, b = 1, 0
    while power3 <= limit:
        weight, a = power3, 0
        while weight <= limit:
            result.append((weight, a, b))
            weight *= 2
            a += 1
        power3 *= 3
        b += 1
    return sorted(result)


def saved_report(path):
    content = path.read_bytes()
    report = json.loads(content)
    rows = report["rows"]
    expected = lattice_points(report["limit"])
    if [row["t"] for row in rows] != [n for n, _, _ in expected]:
        raise AssertionError(f"incomplete smooth-prefix domain in {path}")
    if report["smooth_count"] != len(rows):
        raise AssertionError(f"incorrect smooth count in {path}")
    return report, expected, {
        "path": str(path), "sha256": hashlib.sha256(content).hexdigest(),
        "reported_limit": report["limit"], "smooth_prefixes": len(rows),
    }


def compare(report, points):
    results = []
    weights_by_coordinate = {}
    previous_g = 0
    for index, (saved, (t, a, b)) in enumerate(zip(report["rows"], points), start=1):
        weights_by_coordinate[a, b] = t
        domain = set(weights_by_coordinate)
        corners = [
            {(x, y), (x + 1, y), (x, y + 1)}
            for x, y in domain
            if (x + 1, y) in domain and (x, y + 1) in domain
        ]
        participating = {point for corner in corners for point in corner}
        omitted_classes = [
            {point for point in participating if (point[0] - point[1]) % 3 == j}
            for j in range(3)
        ]
        counts = [len(points_of_colour) for points_of_colour in omitted_classes]
        # Each colour choice is a cover: every corner loses exactly one point.
        for omission in omitted_classes:
            if any(len(corner & omission) != 1 for corner in corners):
                raise AssertionError(f"candidate cover infeasible at {t}")
        # Independent numerical reconstruction of the participating points.
        weights = set(weights_by_coordinate.values())
        numerical_corners = [{n, 2*n, 3*n} for n in weights if 3*n in weights]
        lattice_corners = [
            {weights_by_coordinate[point] for point in corner}
            for corner in corners
        ]
        if {frozenset(c) for c in numerical_corners} != {frozenset(c) for c in lattice_corners}:
            raise AssertionError(f"lattice/numerical corner mismatch at {t}")
        numerical_participating = {n for corner in numerical_corners for n in corner}
        if {weights_by_coordinate[point] for point in participating} != numerical_participating:
            raise AssertionError(f"participation mismatch at {t}")
        # Validate the saved optimum's closed bounds and omission witness.
        g = saved["g"]
        h = index - g
        cover = set(saved["cover"])
        if (saved["points"], saved["minimum_cover_lower"], saved["minimum_cover_upper"]) != (index, h, h):
            raise AssertionError(f"saved exact bounds inconsistent at {t}")
        if len(cover) != h or not cover <= weights:
            raise AssertionError(f"saved optimum cardinality inconsistent at {t}")
        if any(not (corner & cover) for corner in numerical_corners):
            raise AssertionError(f"saved optimum witness infeasible at {t}")
        if saved["jump"] != g - previous_g or g - previous_g not in (0, 1):
            raise AssertionError(f"saved jump inconsistent at {t}")
        previous_g = g
        candidate = index - min(counts)
        difference = g - candidate
        if difference < 0:
            raise AssertionError(f"exact g below achievable candidate at {t}: {g} < {candidate}")
        results.append(dict(zip(FIELDS, (t, g, candidate, difference, index, *counts))))
    return results


def summary(rows):
    discrepancies = [row for row in rows if row["difference"]]
    return {
        "smooth_prefixes": len(rows), "last_smooth_t": rows[-1]["t"],
        "equal_cases": len(rows) - len(discrepancies),
        "difference_counts": dict(sorted(Counter(row["difference"] for row in rows).items())),
        "exact_below_candidate": [row["t"] for row in rows if row["difference"] < 0],
        "discrepancies": discrepancies,
    }


def forcing_comparison(rows, forcing_path, previous_analysis_path):
    forcing = json.loads(forcing_path.read_text())
    forcing_rows = forcing["rows"]
    covered = {row["t"] for row in forcing_rows}
    candidate_rows = {row["t"]: row for row in rows}
    extra_pairs = []
    for row in forcing_rows:
        if candidate_rows[row["t"]]["exact_g"] != row["g"]:
            raise AssertionError(f"forcing report g disagreement at {row['t']}")
        none = [point for point in row["points"] if point["status"] == "none"]
        colours = Counter((point["a"] - point["b"]) % 3 for point in none)
        if len(colours) > 1:
            majority = colours.most_common(1)[0][0]
            off_colour = [point for point in none if (point["a"] - point["b"]) % 3 != majority]
            coordinates = {(point["a"], point["b"]) for point in off_colour}
            if not (len(coordinates) == 2 and any(
                b == 1 and (a + 2, 0) in coordinates for a, b in coordinates
            )):
                raise AssertionError(f"recorded multicolour NONE points are not the extra pair at {row['t']}")
            extra_pairs.append(row["t"])
    previous = json.loads(previous_analysis_path.read_text())
    previous_extra = [row["t"] for row in previous["none_in_multiple_residue_classes"]]
    previous_failures = [row["t"] for row in previous["simple_active_colour_cover_counterexamples"]]
    failures = [row["t"] for row in rows if row["t"] in covered and row["difference"]]
    if extra_pairs != previous_extra or failures != previous_failures:
        raise AssertionError("disagreement with previously recorded membership analysis")
    return {
        "forcing_report": str(forcing_path),
        "previous_analysis": str(previous_analysis_path),
        "classified_prefixes": len(forcing_rows),
        "last_classified_t": forcing_rows[-1]["t"],
        "candidate_failures_in_classified_domain": failures,
        "extra_pair_prefixes": extra_pairs,
        "sets_match_exactly": failures == extra_pairs,
        "candidate_failures_without_forcing_classifications": [
            row["t"] for row in rows if row["t"] not in covered and row["difference"]
        ],
    }


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exact", type=Path, default=Path("experiments/results.json"))
    parser.add_argument("--through", type=int, default=10**11)
    parser.add_argument("--through-exact", type=Path, default=Path("experiments/results-1e11.json"))
    parser.add_argument("--forcing", type=Path, default=Path("experiments/forced-results.json"))
    parser.add_argument("--previous-analysis", type=Path, default=Path("experiments/forced-analysis.json"))
    parser.add_argument("--output", type=Path, default=Path("experiments/candidate-results.json"))
    args = parser.parse_args()
    exact, points, provenance = saved_report(args.exact)
    rows = compare(exact, points)
    requested_rows = [row for row in rows if row["t"] <= args.through]
    through_exact, through_points, through_provenance = saved_report(args.through_exact)
    if through_exact["limit"] != args.through:
        raise AssertionError("requested bound differs from the comparison report limit")
    # Also reconstruct and validate every row of the dedicated 10^11 report.
    if compare(through_exact, through_points) != requested_rows:
        raise AssertionError("exact result files disagree on the requested domain")
    comparison = forcing_comparison(rows, args.forcing, args.previous_analysis)
    report = {
        "candidate": "number of lattice points minus the smallest participating colour class",
        "difference_convention": "exact_g - g_cand",
        "sources": [provenance, through_provenance],
        "verification": {
            "every_colour_cover_checked": True,
            "coordinate_and_numerical_corners_agree": True,
            "saved_exact_bounds_and_witnesses_rechecked": True,
            "exact_reports_agree_on_requested_domain": True,
            "solver_rerun": False, "lean_proof": False,
        },
        "requested_through": args.through,
        "requested_domain": summary(requested_rows),
        "all_saved_domain": summary(rows),
        "forcing_comparison": comparison,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    write_csv(args.output.with_suffix(".csv"), rows)
    write_csv(args.output.with_name(f"{args.output.stem}-through-{args.through}.csv"), requested_rows)
    print(json.dumps({
        "requested_prefixes": len(requested_rows),
        "requested_failures": len(report["requested_domain"]["discrepancies"]),
        "all_saved_prefixes": len(rows),
        "all_saved_failures": len(report["all_saved_domain"]["discrepancies"]),
        "all_saved_difference_counts": report["all_saved_domain"]["difference_counts"],
        "classified_failure_prefixes_match_extra_pairs": comparison["sets_match_exactly"],
    }, indent=2))


if __name__ == "__main__":
    main()
