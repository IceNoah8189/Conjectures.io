#!/usr/bin/env python3
"""Enrich E=1 cutoffs and test interval rules against all saved exact optima.

All powers, floor logarithms, interval tests and ratios use exact integers
or fractions. Decimal strings are only for readable tables.
"""

import argparse
from collections import Counter
import csv
from decimal import Decimal, localcontext
from fractions import Fraction
import json
from pathlib import Path

from candidate_formula import compare, lattice_points, saved_report


def factorization(n):
    a = b = 0
    while n % 2 == 0:
        n //= 2
        a += 1
    while n % 3 == 0:
        n //= 3
        b += 1
    if n != 1:
        raise AssertionError("not 3-smooth")
    return a, b


def power_below(n, base):
    exponent, power = 0, 1
    while power * base <= n:
        power *= base
        exponent += 1
    return exponent, power


def ratio_record(value):
    with localcontext() as context:
        context.prec = 45
        decimal = str(Decimal(value.numerator) / Decimal(value.denominator))
    return {"fraction": str(value), "numerator": value.numerator,
            "denominator": value.denominator, "decimal": decimal}


def local_correction(t, m):
    """Replace three omissions of colour (m+2)%3 with the boundary pair."""
    points = lattice_points(t)
    by_coordinate = {(a, b): n for n, a, b in points}
    domain = set(by_coordinate)
    corners = [
        {(a, b), (a + 1, b), (a, b + 1)}
        for a, b in domain
        if (a + 1, b) in domain and (a, b + 1) in domain
    ]
    active = {point for corner in corners for point in corner}
    colour = (m + 2) % 3
    colour_cover = {point for point in active if (point[0] - point[1]) % 3 == colour}
    removed = {(m + 2, 0), (m + 1, 2), (m + 3, 1)}
    pair = {(m + 1, 1), (m + 3, 0)}
    if not (removed <= colour_cover and pair <= active and not pair & colour_cover):
        raise AssertionError(f"local correction points invalid at {t}")
    cover = (colour_cover - removed) | pair
    if any(not (corner & cover) for corner in corners):
        raise AssertionError(f"local correction leaves a corner at {t}")
    if len(cover) != len(colour_cover) - 1:
        raise AssertionError("incorrect cover improvement")
    return {
        "base_colour": colour,
        "extra_pair": [{"a": a, "b": b, "weight": by_coordinate[a, b]}
                       for a, b in sorted(pair)],
        "removed_omissions": [{"a": a, "b": b, "weight": by_coordinate[a, b]}
                              for a, b in sorted(removed)],
        "corrected_cover": sorted(by_coordinate[point] for point in cover),
        "corrected_set_size": len(points) - len(cover),
    }


RULES = {
    "dyadic_interval_only": "exists m>=0: 24*2^m <= t < 27*2^m",
    "dyadic_interval_and_any_minimum_tie": "dyadic interval and at least two colours minimize c_j",
    "dyadic_interval_and_all_counts_equal": "dyadic interval and c_0=c_1=c_2",
    "dyadic_interval_and_relevant_colour_minimal": "exists m>=0: 24*2^m <= t < 27*2^m and c_((m+2)%3)=min(c_j)",
    "triadic_10_to_12_interval": "exists j>=0: 10*3^j <= t < 12*3^j",
}


def predictions(t, counts):
    k = t.bit_length() - 1
    m = k - 4
    inside = m >= 0 and 24 * 2**m <= t < 27 * 2**m
    minimum_colours = [j for j, count in enumerate(counts) if count == min(counts)]
    triadic = False
    power = 1
    while 10 * power <= t:
        if t < 12 * power:
            triadic = True
            break
        power *= 3
    return m, minimum_colours, {
        "dyadic_interval_only": inside,
        "dyadic_interval_and_any_minimum_tie": inside and len(minimum_colours) >= 2,
        "dyadic_interval_and_all_counts_equal": inside and len(minimum_colours) == 3,
        "dyadic_interval_and_relevant_colour_minimal": inside and (m + 2) % 3 in minimum_colours,
        "triadic_10_to_12_interval": triadic,
    }


def analyze(rows):
    rules = {name: {"definition": definition, "true_positives": 0,
                    "false_positives": [], "false_negatives": [], "mismatches": []}
             for name, definition in RULES.items()}
    details, evaluations = [], []
    local_corrections = 0
    for row in rows:
        t = row["t"]
        counts = [row[f"c_{j}"] for j in range(3)]
        m, minima, predicted = predictions(t, counts)
        actual = row["difference"]
        if actual not in (0, 1):
            raise AssertionError("binary rules require E in {0,1}; saved data differs")
        evaluations.append({"t": t, "actual_E": actual,
                            **{name: int(value) for name, value in predicted.items()}})
        for name, value in predicted.items():
            rule = rules[name]
            if value and actual:
                rule["true_positives"] += 1
            if int(value) != actual:
                mismatch = {"t": t, "actual_E": actual, "predicted_E": int(value),
                            "c": counts, "m": m, "relevant_colour": (m + 2) % 3}
                rule["mismatches"].append(mismatch)
                rule["false_positives" if value else "false_negatives"].append(t)
        if predicted["dyadic_interval_only"]:
            correction = local_correction(t, m)
            local_corrections += 1
            if correction["corrected_set_size"] > row["exact_g"]:
                raise AssertionError(f"feasible correction exceeds saved optimum at {t}")
        if not actual:
            continue
        if not predicted["dyadic_interval_only"]:
            raise AssertionError(f"no proposed boundary pair at E=1 cutoff {t}")
        if correction["corrected_set_size"] != row["exact_g"]:
            raise AssertionError(f"corrected cover not optimal at {t}")
        a, b = factorization(t)
        k, p2 = power_below(t, 2)
        j, p3 = power_below(t, 3)
        if k != t.bit_length() - 1:
            raise AssertionError("floor-log2 implementations disagree")
        details.append({
            **row, "a": a, "b": b, "m": m,
            "minimum_colours": minima, "minimum_tied": len(minima) >= 2,
            "floor_log2": k, "floor_log3": j,
            "ratio2": ratio_record(Fraction(t, p2)),
            "ratio3": ratio_record(Fraction(t, p3)),
            **correction,
        })
    return {
        "prefix_count": len(rows), "last_t": rows[-1]["t"],
        "excess_cutoffs": len(details),
        "local_corrections_checked": local_corrections,
        "minimum_multiplicity_counts_at_excess": dict(Counter(len(d["minimum_colours"]) for d in details)),
        "rules": rules, "details": details, "evaluations": evaluations,
        "interpretation": "Finite rule fit. The local swap constructs a feasible improved set; no general necessity/upper bound or Lean proof is claimed.",
    }


def write_csv(path, details):
    fields = ["t", "a", "b", "exact_g", "g_cand", "E", "m", "base_colour",
              "pair_a1", "pair_b1", "pair_weight1", "pair_a2", "pair_b2", "pair_weight2",
              "c_0", "c_1", "c_2", "minimum_colours", "minimum_tied",
              "floor_log2", "floor_log3", "ratio2_exact", "ratio2_decimal",
              "ratio3_exact", "ratio3_decimal"]
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for detail in details:
            first, second = detail["extra_pair"]
            writer.writerow({
                **{key: detail[key] for key in
                   ["t", "a", "b", "exact_g", "g_cand", "m", "base_colour",
                    "c_0", "c_1", "c_2", "minimum_tied", "floor_log2", "floor_log3"]},
                "E": detail["difference"],
                "minimum_colours": "|".join(map(str, detail["minimum_colours"])),
                "pair_a1": first["a"], "pair_b1": first["b"], "pair_weight1": first["weight"],
                "pair_a2": second["a"], "pair_b2": second["b"], "pair_weight2": second["weight"],
                "ratio2_exact": detail["ratio2"]["fraction"],
                "ratio2_decimal": detail["ratio2"]["decimal"],
                "ratio3_exact": detail["ratio3"]["fraction"],
                "ratio3_decimal": detail["ratio3"]["decimal"],
            })


def markdown_table(details):
    lines = ["| t | Factorization | Extra omitted pair (a,b) | (c0,c1,c2) | Minimizers | t / 2^floor(log2 t) | t / 3^floor(log3 t) |",
             "| ---: | --- | --- | --- | --- | ---: | ---: |"]
    for d in details:
        pair = ", ".join(f"({point['a']},{point['b']})" for point in d["extra_pair"])
        counts = ",".join(str(d[f"c_{j}"]) for j in range(3))
        minima = ",".join(map(str, d["minimum_colours"]))
        if d["minimum_tied"]:
            minima += " (tie)"
        else:
            minima += " (unique)"
        r2 = f"{Decimal(d['ratio2']['decimal']):.9f}"
        r3 = f"{Decimal(d['ratio3']['decimal']):.9f}"
        lines.append(f"| {d['t']} | 2^{d['a']} * 3^{d['b']} | {pair} | ({counts}) | {minima} | {r2} | {r3} |")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exact", type=Path, default=Path("experiments/results.json"))
    parser.add_argument("--comparison", type=Path, default=Path("experiments/candidate-results.json"))
    parser.add_argument("--output", type=Path, default=Path("experiments/excess-results.json"))
    args = parser.parse_args()
    exact, points, provenance = saved_report(args.exact)
    rows = compare(exact, points)
    if rows != json.loads(args.comparison.read_text())["rows"]:
        raise AssertionError("saved comparison disagrees with fresh reconstruction")
    report = analyze(rows)
    report["exact_source"] = provenance
    report["comparison_source"] = str(args.comparison)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    write_csv(args.output.with_suffix(".csv"), report["details"])
    args.output.with_suffix(".md").write_text(markdown_table(report["details"]))
    print(json.dumps({
        "cutoffs": report["prefix_count"], "excess_cutoffs": report["excess_cutoffs"],
        "local_corrections_checked": report["local_corrections_checked"],
        "minimum_multiplicity_counts": report["minimum_multiplicity_counts_at_excess"],
        "mismatch_counts": {name: len(rule["mismatches"]) for name, rule in report["rules"].items()},
    }, indent=2))


if __name__ == "__main__":
    main()
