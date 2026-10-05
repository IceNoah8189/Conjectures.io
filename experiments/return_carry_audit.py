#!/usr/bin/env python3
"""Round 3 exact boundary-return audit. No optimizer and no Lean.

The participating-colour recurrence is unconditional. Jump values and all
density interpretations use the frozen minimum/excess rule. Integers decide
every inequality; displayed logarithms are not used in the verification.
"""

import argparse
from math import comb
import csv
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from time import monotonic

from candidate_formula import lattice_points
from colour_imbalance import row_colours, row_formula


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pure3_jump(t, b, counts):
    """At b>=4, the only birth at 3^b is the point of colour -b.

    Such a power is never a dyadic-window endpoint: unique factorization
    excludes 3^b=24*2^m or 27*2^m when b>=4. Thus the same interval
    membership can be used on both sides of the birth.
    """
    assert b >= 4
    before = counts.copy()
    before[(-b) % 3] -= 1
    h0, h1 = min(before), min(counts)
    m = t.bit_length() - 5
    inside = m >= 0 and 24 * 2**m <= t < 27 * 2**m
    j = (m + 2) % 3
    E0 = int(inside and before[j] == h0)
    E1 = int(inside and counts[j] == h1)
    jump = 1 - (h1 - h0) + E1 - E0
    assert jump in (0, 1)
    return jump


def check_fractional_cover():
    path = Path("experiments/gate1-fractional-cover.json")
    certificate = json.loads(path.read_text())
    t = certificate["t"]
    points = lattice_points(t)
    values = {(a, b): Fraction(z) for a, b, z in certificate["cover"]}
    domain = {(a, b) for _, a, b in points}
    assert len(values) == len(certificate["cover"]) and set(values) == domain
    assert all(0 <= z <= 1 for z in values.values())
    corners = [[(a, b), (a+1, b), (a, b+1)] for a, b in domain
               if (a+1, b) in domain and (a, b+1) in domain]
    assert all(sum(values[v] for v in e) >= 1 for e in corners)
    cost = sum(values.values())
    assert cost == Fraction(certificate["feasible_fractional_cover_cost"])
    counts = row_formula(t)[0]
    h, m = min(counts), t.bit_length()-5
    E = int(m >= 0 and 24*2**m <= t < 27*2**m and counts[(m+2) % 3] == h)
    assert h-E == certificate["rule_minimum_integer_cover"] == 26
    assert cost < h-E-1
    exact_path = Path("experiments/results-1e14.json")
    saved = next(r for r in json.loads(exact_path.read_text())["rows"] if r["t"] == t)
    assert saved["minimum_cover_lower"] == saved["minimum_cover_upper"] == 26
    cover = set(saved["cover"])
    weights = {(a,b): w for w,a,b in points}
    assert len(cover) == 26 and cover <= set(weights.values())
    assert all(any(weights[v] in cover for v in e) for e in corners)
    return {"t": t, "points": len(points), "corners": len(corners),
            "fractional_feasible_cost": str(cost), "saved_integer_cover_size": 26,
            "certificate_source_sha256": sha(path),
            "saved_integer_source_sha256": sha(exact_path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--through", type=int, default=131072)
    parser.add_argument("--output", type=Path,
                        default=Path("experiments/return-carry-audit.json"))
    args = parser.parse_args()
    start = monotonic()
    gate1 = check_fractional_cover()
    frozen_path = Path("experiments/predicted-1e14.json")
    frozen = json.loads(frozen_path.read_text())
    assert sha(Path("experiments/excess_rule.py")) == frozen["rule_source_sha256"]
    saved_path = Path("experiments/colour-imbalance-powers3.csv")
    with saved_path.open(newline="") as f:
        saved = {int(r["k"]): r for r in csv.DictReader(f)}
    checks = {4, 205, 665, 904, 1995, 2285, 2286, 4096, 8192,
              15601, 16384, 31867, 32768, 65536, 131072, args.through}
    sums, word_counts, power3, zeros, matches = [0, 0, 0], [0, 0, 0], 1, [], 0
    d_values = [0]
    ones = 0
    checkpoints, zero_runs, run = [], [], None
    recurrence_checks = 0
    return_data = []
    # All these pairs are from the previously integer-certified CF prefix.
    # The multiplier 3 enforces p+q=0 modulo 3 when necessary.
    returns = [(252, 159), (1455, 918), (1054, 665),
               (74181, 46803)]
    boundary_counts = {pair: [0, 0, 0] for pair in returns}
    thresholds = {(p, q, r): (1 << ((4+r)*p)) * 3**(4*q)
                  for p, q in returns for r in (1, 2, 3)}
    for b in range(1, args.through + 1):
        n, N = b - 1, power3.bit_length()
        residue = row_colours(N, -n)
        sums = [c + r for c, r in zip(sums, residue)]
        word_counts[(N-1+n) % 3] += 1
        A, B = sums[0]-sums[2], sums[1]-sums[2]
        W0, W1 = word_counts[0]-word_counts[2], word_counts[1]-word_counts[2]
        cyclic = row_colours(b, 0)
        V0, V1 = cyclic[0]-cyclic[2], cyclic[1]-cyclic[2]
        assert (A+B, 2*B-A) == (V0+W1, V1-W0+W1)
        row0 = row_colours(N + 1, 0)
        counts = [sums[(j + b) % 3] + row0[j] for j in range(3)]
        d_values.append(sum(counts)-3*min(counts))
        power3 *= 3
        if b in saved:
            assert counts == [int(saved[b][f"c_{j}"]) for j in range(3)]
            matches += 1
        if b in checks and b <= 8192:
            assert counts == row_formula(power3)[0]
            recurrence_checks += 1
        if b < 4:
            continue
        jump = pure3_jump(power3, b, counts)
        if jump:
            ones += 1
            if run is not None:
                zero_runs.append(run)
                run = None
        else:
            zeros.append(b)
            if run is None:
                run = [b, b]
            else:
                run[1] = b
        # At a=-r*p, kappa_r(a,b)=epsilon(0,b). If T>=4s,
        # 2^(r*p)/3^b >= exp(-4s) iff
        # 3^b <= 2^((4+r)*p)*3^(4*q). Integer comparison certifies it.
        for p, q in returns:
            if jump:
                for r in (1, 2, 3):
                    if b <= 4 * q or power3 <= thresholds[p, q, r]:
                        boundary_counts[p, q][r-1] += 1
        if b in checks:
            u, v = counts[0]-counts[1], counts[1]-counts[2]
            checkpoints.append({"b": b, "ones_b_4_to_b": ones,
                                "zeros_b_4_to_b": len(zeros),
                                "last_zero": zeros[-1] if zeros else None,
                                "D": [u, v],
                                "d": sum(counts)-3*min(counts)})
    if run is not None:
        zero_runs.append(run)
    assert matches == min(args.through, max(saved))
    for p, q in returns:
        return_data.append({"p": p, "q": q, "colour_shift_mod3": (p+q)%3,
                            "boundary_nonzero_lower_bounds_r_1_2_3": boundary_counts[p,q],
                            "scope": "Lower bounds from b>=4 on one boundary slice only; partial if the slice extends beyond --through."})
    differences = []
    for shift in (159, 477, 665, 918, 1995, 2754):
        for end in sorted({min(args.through, 8192),
                           min(args.through, 11*shift), args.through}):
            for r in (1, 2, 3):
                nz, first, largest, tested = 0, None, 0, 0
                for k in range(shift, end-r*shift+1):
                    value = sum((-1)**(r-j)*comb(r,j)*d_values[k+j*shift]
                                for j in range(r+1))
                    tested += 1
                    if value:
                        nz += 1
                        if first is None:
                            first = {"k": k, "value": value,
                                     "d_at_shifted_points": [d_values[k+j*shift]
                                                              for j in range(r+1)]}
                        largest = max(largest, abs(value))
                differences.append({"shift": shift, "order": r, "through_b": end,
                                    "tested_start_indices": tested, "nonzero": nz,
                                    "first_nonzero": first, "max_absolute_value": largest})
    report = {
        "interpretation": "Exact conditional frozen-rule jump data; not a proof of the global rule or irrationality.",
        "through_b": args.through,
        "last_power3_bit_length": power3.bit_length(),
        "saved_row_count_matches": matches,
        "independent_closed_row_checks": recurrence_checks,
        "exact_rotation_word_identity_checks": args.through,
        "ones": ones, "zeros": len(zeros),
        "first_zero_after_2285": next((b for b in zeros if b>2285), None),
        "zero_runs": zero_runs,
        "zero_indices": zeros,
        "checkpoints": checkpoints,
        "returns": return_data,
        "pure_power_d_finite_differences": differences,
        "gate1_fractional_cover_exact_check": gate1,
        "frozen_rule_source_sha256": sha(Path("experiments/excess_rule.py")),
        "saved_row_source_sha256": sha(saved_path),
        "program_source_sha256": sha(Path(__file__)),
        "row_program_source_sha256": sha(Path("experiments/colour_imbalance.py")),
        "elapsed_seconds": monotonic() - start,
    }
    args.output.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps({k: report[k] for k in (
        "through_b", "last_power3_bit_length", "saved_row_count_matches",
        "independent_closed_row_checks", "ones", "zeros",
        "first_zero_after_2285", "checkpoints", "returns", "elapsed_seconds")}, indent=2))


if __name__ == "__main__":
    main()
