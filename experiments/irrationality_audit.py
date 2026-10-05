#!/usr/bin/env python3
"""Round 2: exact tail bounds for the frozen rule, without an optimizer.

All decisions use integers/Fraction. Decimal is display only. The extension
beyond the saved solver domain is conditional on the frozen rule. This
program does not certify irrationality or rerun external solver claims.
"""

import argparse
import csv
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from candidate_formula import lattice_points
from colour_imbalance import birth


def display(x):
    x = Fraction(x)
    with localcontext() as ctx:
        ctx.prec = 110
        return str(Decimal(x.numerator) / Decimal(x.denominator))


def record(x):
    return {"fraction": str(x), "decimal": display(x)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def distance_interval(lo, hi):
    """Certified minimum distance of the closed interval from Z."""
    n = lo.numerator // lo.denominator
    if lo == n or hi >= n + 1:
        return Fraction(0)
    return min(lo - n, n + 1 - hi)


def simplest_rational(lo, hi):
    """Accelerated Stern--Brocot; parents certify minimum denominator."""
    assert 0 < lo <= hi < 1
    a, b, c, d = 0, 1, 1, 0
    while True:
        m = Fraction(a + c, b + d)
        if m < lo:
            k = (lo.numerator*b - lo.denominator*a - 1) // (
                lo.denominator*c - lo.numerator*d)
            assert k >= 1
            a, b = a + k*c, b + k*d
        elif m > hi:
            k = (hi.denominator*c - hi.numerator*d - 1) // (
                hi.numerator*b - hi.denominator*a)
            assert k >= 1
            c, d = c + k*a, d + k*b
        else:
            assert b*c - a*d == 1
            assert Fraction(a, b) < lo <= m <= hi
            assert d and hi < Fraction(c, d)
            return {"first_rational_in_interval": str(m),
                    "minimum_denominator": m.denominator,
                    "left_parent": str(Fraction(a, b)),
                    "right_parent": str(Fraction(c, d)),
                    "interpretation": "Every rational in this interval has at least this denominator; this is a finite bound."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--through", type=int, default=160)
    parser.add_argument("--output", type=Path, default=Path("experiments/irrationality-audit.json"))
    parser.add_argument("--oeis-table", type=Path)
    args = parser.parse_args()
    if args.through < 100:
        raise ValueError("this audit needs --through >= 100 for its fixed rectangle and denominator checks")
    limit = 54 * 4**args.through
    frozen_path = Path("experiments/predicted-1e14.json")
    frozen = json.loads(frozen_path.read_text())
    assert sha(Path("experiments/excess_rule.py")) == frozen["rule_source_sha256"]
    exact_path = Path("experiments/results-1e14.json")
    exact = json.loads(exact_path.read_text())
    saved = {r["t"]: r for r in exact["rows"]}
    counts, h, E, g = [0, 0, 0], 0, 0, 0
    all_mass = S = Fraction(0)
    rows, digits, matched = [], {}, 0
    for index, (t, a, b) in enumerate(lattice_points(limit), 1):
        birth(t, a, b, counts)
        next_h = min(counts)
        m = t.bit_length() - 5
        inside = m >= 0 and 24*2**m <= t < 27*2**m
        next_E = int(inside and counts[(m + 2) % 3] == next_h)
        jump = 1 - (next_h - h) + (next_E - E)
        assert jump in (0, 1)
        g += jump
        if t in saved:
            assert g == saved[t]["g"] and jump == saved[t]["jump"]
            matched += 1
        digits[a, b] = jump
        rows.append((t, a, b, jump, g))
        all_mass += Fraction(1, t)
        S += Fraction(jump, t)
        h, E = next_h, next_E
    assert matched == len(saved)
    tail = 3 - all_mass
    # Independently sum infinite geometric row tails, including absent rows.
    row_tail = Fraction(0)
    p3, Bmax = 1, -1
    while p3 <= limit:
        Amax = (limit // p3).bit_length() - 1
        row_tail += Fraction(1, 2**Amax * p3)
        p3 *= 3
        Bmax += 1
    row_tail += Fraction(1, 3**Bmax)
    assert tail == row_tail and tail > 0

    def rectangle(A, B, q=1):
        D = 2**A * 3**B
        assert D <= limit  # whole rectangle is inside the computed domain
        head = sum((Fraction(j, t) for t, a, b, j, _ in rows
                    if a <= A and b <= B), Fraction(0))
        assert (D*head).denominator == 1
        lo, hi = q*D*(S - head), q*D*(S - head + tail)
        upper = q*(2**A + Fraction(3, 2)*3**B - Fraction(1, 2))
        all_rectangle = (2 - Fraction(1, 2**A)) * (
            Fraction(3, 2) - Fraction(1, 2*3**B))
        assert q*D*(3 - all_rectangle) == upper
        lower = q*3**B  # all powers of two jump
        assert lower <= lo <= hi <= upper
        margin = distance_interval(lo, hi)
        return {"A": A, "B": B, "q": q,
                "cleared_rectangle_head": str(q*D*head),
                "tail_lower": str(lo), "tail_upper": str(hi),
                "tail_lower_display": display(lo),
                "all_smooth_tail_upper_display": display(upper),
                "certified_width": str(hi - lo),
                "fractional_part_lower": str(lo % 1),
                "fractional_part_display": display(lo % 1),
                "distance_from_integers_lower": str(margin),
                "distance_display": display(margin)}

    convergents = [(1, 1), (2, 1), (3, 2), (8, 5), (19, 12), (65, 41), (84, 53)]
    conv = [rectangle(A, B) for A, B in convergents if 2**A*3**B <= limit]
    # Balanced rectangles; retain comfortable precision for the modulo test.
    balanced = []
    for A in range(1, 141):
        p3, B = 1, 0
        while 3*p3 <= 2**A:
            p3 *= 3
            B += 1
        if 2**A*p3 <= limit:
            balanced.append(rectangle(A, B))
    clear = [r for r in balanced if Fraction(r["distance_from_integers_lower"]) > 0]
    near = min(clear, key=lambda r: Fraction(r["distance_from_integers_lower"]))
    # One fixed convergent: this excludes only the tested denominators.
    A, B = 84, 53
    q_margins = [(distance_interval(q*2**A*3**B*S,
                                  q*2**A*3**B*(S + tail)), q)
                 for q in range(1, 1001)]
    assert all(margin > 0 for margin, _ in q_margins)
    smallest_margin, closest_q = min(q_margins)

    # Raw direct return matching. This is not a test of every regrouping.
    returns = []
    for p, q in [(19, 12), (65, 41), (84, 53), (57, 36), (195, 123), (252, 159)]:
        checkpoints = []
        for K in sorted({20, 40, 80, 120, args.through}):
            if K > args.through:
                continue
            bound = 54*4**K
            comparisons = []
            for t, a, b, j, _ in rows:
                if b >= q + 2 and t <= bound:
                    aa, bb = a + p, b - q
                    if (aa, bb) in digits and 2**aa*3**bb <= bound:
                        comparisons.append((t, j, digits[aa, bb]))
            mismatch = [x for x in comparisons if x[1] != x[2]]
            checkpoints.append({"K": K, "pairs": len(comparisons),
                                "mismatches": len(mismatch),
                                "first_mismatch_t": mismatch[0][0] if mismatch else None})
        returns.append({"p": p, "q": q, "colour_shift_mod3": (p + q) % 3,
                        "weight_ratio": str(Fraction(2**p, 3**q)),
                        "checkpoints": checkpoints})

    external = None
    if args.oeis_table:
        entries = [tuple(map(int, line.split())) for line in args.oeis_table.read_text().splitlines()
                   if line.strip() and not line.startswith("#")]
        assert [n for n, _ in entries] == list(range(1, len(entries) + 1))
        expected = [k for _, k in entries]
        end = expected[-1]
        observed = [i for i, row in enumerate(rows[:end], 1) if row[3]]
        external = {"url": "https://oeis.org/A004059/b004059.txt",
                    "sha256": sha(args.oeis_table), "entries": len(entries),
                    "last_first_hit_index": end, "matches": observed == expected,
                    "first_mismatch": next(((i, x, y) for i, (x, y) in
                                             enumerate(zip(expected, observed), 1) if x != y), None),
                    "scope": "Agreement with external tabulated computation, not a new solver certificate."}
    frontier = {k: rows[k - 1][4] for k in range(5000, 5021)}
    published_first_hits = [5002, 5003, 5005, 5007, 5008, 5010, 5012, 5014, 5015, 5017, 5018, 5019]
    assert [k for k in range(5001, 5021) if rows[k - 1][3]] == published_first_hits
    assert frontier[5000] == 3335 and frontier[5020] == 3347

    actualS = sum((Fraction(r["jump"], r["t"]) for r in exact["rows"]), Fraction(0))
    actual_tail = 3 - sum((Fraction(1, r["t"]) for r in exact["rows"]), Fraction(0))
    report = {
        "scope": f"Frozen-rule arithmetic through 54*4^{args.through}; universal irrationality is unresolved.",
        "limit": limit, "smooth_points": len(rows), "jumps": g,
        "saved_solver_prefixes_matched": matched,
        "sources": {str(p): sha(p) for p in [Path(__file__), Path("experiments/colour_imbalance.py"),
                      Path("experiments/excess_rule.py"), exact_path, frozen_path]},
        "S_partial": record(S), "L_partial": record(S/3),
        "all_smooth_reciprocal_tail": record(tail),
        "frozen_density_denominator_certificate": simplest_rational(S/3, (S + tail)/3),
        "saved_actual_density_denominator_certificate": simplest_rational(actualS/3, (actualS + actual_tail)/3),
        "convergent_rectangles": conv,
        "balanced_rectangles": {"count": len(balanced), "all_exclude_q1": len(clear) == len(balanced),
                                "closest_to_integer": near},
        "q1_through_1000_at_84_53": {"all_excluded": True, "closest_q": closest_q,
                                    "minimum_certified_margin": record(smallest_margin)},
        "raw_translation_returns": returns,
        "external_oeis_comparison": external,
        "published_frontier_rule_values": frontier,
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    csv_path = args.output.with_suffix(".csv")
    with csv_path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(balanced[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(balanced)
    print(json.dumps({"smooth_points": len(rows), "jumps": g, "matched": matched,
                      "L_partial": display(S/3), "tail": display(tail),
                      "closest_balanced": [near["A"], near["B"], near["distance_display"]],
                      "closest_q": closest_q, "q_margin": display(smallest_margin),
                      "external_oeis": external, "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
