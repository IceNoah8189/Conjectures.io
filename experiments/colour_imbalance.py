#!/usr/bin/env python3
"""Exact row formula for participating colours; no optimizer or Lean.

The colour counts themselves are unconditional lattice identities. Only
comparisons with g and the density interpretation use the frozen rule.
"""

import argparse
from fractions import Fraction
import json
from pathlib import Path

from candidate_formula import compare, lattice_points, saved_report
from density_expansion import source


# Columns are b mod 3; rows are A_b mod 3. A full triple cancels.
F = (
    ((1, 0), (0, -1), (-1, 1)),
    ((0, 1), (1, -1), (-1, 0)),
    ((0, 0), (0, 0), (0, 0)),
)
BOUNDARY = ((1, 0), (0, 0), (1, -1))  # (A_1+1) mod 3


def row_colours(length, b):
    """Colours of a=0,...,length-1 in row b, using exact divmod."""
    triples, remainder = divmod(length, 3)
    result = [triples] * 3
    for a in range(remainder):
        result[(a-b) % 3] += 1
    return result


def row_formula(t):
    """Return counts, D, and all row lengths without any logarithms."""
    if t < 3:
        return [0, 0, 0], (0, 0), []
    # floor(log_2(t // 3^b)) is floor(log_2(t / 3^b)).
    power3, b, lengths = 3, 1, []
    while power3 <= t:
        lengths.append((t // power3).bit_length())
        power3 *= 3
        b += 1
    counts = row_colours(lengths[0]+1, 0)
    D = list(BOUNDARY[lengths[0] % 3])
    for b, length in enumerate(lengths, start=1):
        row = row_colours(length, b)
        counts = [c+r for c, r in zip(counts, row)]
        if b >= 2:
            vector = F[(length-1) % 3][b % 3]
            D = [d+v for d, v in zip(D, vector)]
    if tuple(D) != (counts[0]-counts[1], counts[1]-counts[2]):
        raise AssertionError(f"row vector table fails at {t}")
    return counts, tuple(D), lengths


def birth(t, a, b, counts):
    """Independent local participation increments from complete corners."""
    if b == 1:
        counts[(a-1) % 3] += 1
        counts[(a+1) % 3] += 1
        if a == 0:
            counts[0] += 1
    elif b >= 2:
        counts[(a-b) % 3] += 1


def verify(limit):
    frozen_path = Path("experiments/predicted-1e14.json")
    frozen = json.loads(frozen_path.read_text())
    rule_source = source(Path("experiments/excess_rule.py"))
    if rule_source["sha256"] != frozen["rule_source_sha256"]:
        raise AssertionError("frozen participation/excess source changed")
    exact, saved_points, exact_source = saved_report(Path("experiments/results-1e14.json"))
    independent = {r["t"]: r for r in compare(exact, saved_points)}
    counts, g, matches, checked = [0, 0, 0], 0, 0, 0
    oldh, oldE, oldd, k, power3 = 0, 0, 0, 0, 1
    coefficients = {}
    for t, a, b in lattice_points(limit):
        birth(t, a, b, counts)
        row_counts, D, lengths = row_formula(t)
        if counts != row_counts:
            raise AssertionError(f"birth and closed row counts disagree at {t}")
        h = min(counts)
        d = sum(counts)-3*h
        if d != max(-2*D[0]-D[1], D[0]-D[1], D[0]+2*D[1]):
            raise AssertionError(f"D-to-d identity fails at {t}")
        m = t.bit_length()-5
        E = int(m >= 0 and 24*2**m <= t < 27*2**m and counts[(m+2) % 3] == h)
        jump = 1-(h-oldh)+(E-oldE)
        if jump not in (0, 1) or abs(d-oldd) > 2:
            raise AssertionError(f"frozen increment bounds fail at {t}")
        g += jump
        if t in independent:
            saved = independent[t]
            if counts != [saved[f"c_{j}"] for j in range(3)] or g != saved["exact_g"]:
                raise AssertionError(f"saved solver/corner mismatch at {t}")
            matches += 1
        while power3*3 <= t:
            k, power3 = k+1, power3*3
        coefficients[k] = coefficients.get(k, Fraction(0))+Fraction((d-oldd)*power3, t)
        oldh, oldE, oldd = h, E, d
        checked += 1
    if matches != len(independent):
        raise AssertionError("not every saved solver cutoff was checked")
    audit_path = Path("experiments/density-expansion-audit.csv")
    import csv
    with audit_path.open(newline="") as stream:
        audited = list(csv.DictReader(stream))
    for row in audited:
        if coefficients[int(row["k"])] != Fraction(row["b_nearest_rational"]):
            raise AssertionError(f"saved nearest-power coefficient differs at k={row['k']}")
    return {
        "interpretation": "Row identities are unconditional for participating lattice points; g comparisons use the frozen rule, not a proof of it.",
        "limit": limit, "all_smooth_cutoffs_checked": checked,
        "all_saved_solver_cutoffs_checked": matches,
        "saved_nearest_power_coefficients_checked": len(audited),
        "last_cutoff": {"t": t, "a": a, "b": b, "counts": counts, "D": D, "d": oldd},
        "F_rows_A_mod_3_columns_b_mod_3": F,
        "boundary_rows_N1_mod_3": BOUNDARY,
        "rule_source": rule_source, "exact_source": exact_source,
        "saved_audit_source": source(audit_path), "program_source": source(Path(__file__)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--through", type=int, default=160)
    parser.add_argument("--output", type=Path, default=Path("experiments/colour-imbalance-verification.json"))
    args = parser.parse_args()
    if args.through < 160:
        raise ValueError("the saved coefficient audit requires through >= 160")
    report = verify(54*4**args.through)
    args.output.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({key: report[key] for key in (
        "all_smooth_cutoffs_checked", "all_saved_solver_cutoffs_checked",
        "saved_nearest_power_coefficients_checked", "last_cutoff")}, indent=2))


if __name__ == "__main__":
    main()
