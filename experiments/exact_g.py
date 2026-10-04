#!/usr/bin/env python3
"""Independent exact Boolean hitting-set computation for Erdos 168.

No column states, bitmask DP, tabulated optima, or conjectural jump rule
are used. Z3 solves a Boolean MaxSAT formula. Fractions keep
the density sum and its smooth-number tail bound exact.
"""

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import json
from pathlib import Path
import time

import z3


EXPECTED_JUMPS = (
    1, 2, 4, 6, 8, 12, 16, 24, 32, 36, 48, 64, 72, 96,
    128, 144, 162, 216, 256, 288,
)
EXPECTED_DENSITY = Fraction("0.8009657549")


def smooth_points(limit):
    """Return (weight, a, b), sorted using integer arithmetic only."""
    points = []
    power3, b = 1, 0
    while power3 <= limit:
        weight, a = power3, 0
        while weight <= limit:
            points.append((weight, a, b))
            weight *= 2
            a += 1
        power3 *= 3
        b += 1
    return sorted(points)


def checked_cover(weights, cover, triples):
    """Check the returned witness independently of the SAT model."""
    cover = set(cover)
    domain = set(weights)
    if not cover <= domain:
        raise AssertionError("witness contains a point outside the domain")
    numerical_triples = {(n, 2*n, 3*n) for n in weights if 3*n in domain}
    if set(triples) != numerical_triples:
        raise AssertionError("lattice constraints differ from numerical triples")
    if any(not (cover & set(triple)) for triple in numerical_triples):
        raise AssertionError("witness fails to hit a forbidden triple")


def exact_prefix(limit, timeout_ms=0, progress=False):
    """Compute g at every smooth point up to limit, with cover witnesses.

    Corner clauses are hard constraints; each non-omitted vertex is a
    unit-weight soft constraint. The exact minimum soft cost is the
    minimum number of omissions. Check matching integer lower and upper
    bounds and the returned cover; UNKNOWN aborts the computation.
    """
    solver = z3.Optimize()
    solver.set(maxsat_engine="maxres")
    if timeout_ms:
        solver.set(timeout=timeout_ms)
    variables, positions, weights, triples = [], {}, [], []
    minimum, rows, objective = 0, [], None
    for weight, a, b in smooth_points(limit):
        started = time.perf_counter()
        variables.append(z3.Bool(f"omit_{a}_{b}"))
        # With the same default objective id, all soft clauses sum to
        # one objective: each omitted point has cost one.
        handle = solver.add_soft(z3.Not(variables[-1]), weight=1)
        if objective is None:
            objective = handle
        positions[a, b] = len(weights)
        weights.append(weight)
        # Any corner containing the new point has one of these anchors.
        for x, y in ((a, b), (a - 1, b), (a, b - 1)):
            corner = ((x, y), (x + 1, y), (x, y + 1))
            if all(point in positions for point in corner):
                indices = [positions[point] for point in corner]
                solver.add(z3.Or(*(variables[i] for i in indices)))
                triples.append(tuple(weights[i] for i in indices))
        previous_minimum = minimum
        result = solver.check()
        if result != z3.sat:
            raise RuntimeError(
                f"no exact result at t={weight}: {solver.reason_unknown()}"
            )
        lower, upper = solver.lower(objective), solver.upper(objective)
        if not (z3.is_int_value(lower) and z3.is_int_value(upper)
                and lower.as_long() == upper.as_long()):
            raise RuntimeError(f"unclosed objective at {weight}: {lower}, {upper}")
        minimum = lower.as_long()
        if minimum not in (previous_minimum, previous_minimum + 1):
            raise AssertionError("minimum cover violates one-point bound")
        model = solver.model()
        cover = {
            n for n, variable in zip(weights, variables)
            if z3.is_true(model.eval(variable, model_completion=True))
        }
        checked_cover(weights, cover, triples)
        if len(cover) != minimum:
            raise AssertionError("incorrect witness cardinality")
        row = {
            "t": weight,
            "points": len(weights),
            "g": len(weights) - minimum,
            "jump": int(minimum == previous_minimum),
            "cover": sorted(cover),
            "minimum_cover_lower": minimum,
            "minimum_cover_upper": upper.as_long(),
            "seconds": round(time.perf_counter() - started, 6),
        }
        rows.append(row)
        if progress and (len(rows) % 25 == 0 or row["seconds"] > 1):
            print(f"points={len(rows)} t={weight} g={row['g']} "
                  f"cover={minimum} seconds={row['seconds']}", flush=True)
    return rows


def g_from_rows(rows, t):
    """g(0)=0; the domain changes only at smooth integers."""
    return next((row["g"] for row in reversed(rows) if row["t"] <= t), 0)


def brute_g(t):
    """Separate exhaustive enumeration oracle for small domains.

    Enumerate all subsets of the numerical smooth integers and check
    {n,2n,3n} directly. This is not the lattice constraint generator.
    """
    weights = [n for n, _, _ in smooth_points(t)]
    positions = {n: i for i, n in enumerate(weights)}
    triple_masks = [
        (1 << positions[n]) | (1 << positions[2*n]) | (1 << positions[3*n])
        for n in weights if 3*n <= t
    ]
    best = 0
    for subset in range(1 << len(weights)):
        size = subset.bit_count()
        if size > best and all(subset & triple != triple for triple in triple_masks):
            best = size
    return best


def fraction_record(value):
    with localcontext() as context:
        context.prec = 50
        decimal = str(Decimal(value.numerator) / Decimal(value.denominator))
    return {"numerator": value.numerator, "denominator": value.denominator,
            "decimal": decimal}


def make_report(limit, rows, brute_limit):
    if brute_limit > limit:
        raise ValueError("brute-force limit must not exceed computation limit")
    for t in range(brute_limit + 1):
        actual, expected = g_from_rows(rows, t), brute_g(t)
        if actual != expected:
            raise AssertionError(f"brute-force disagreement at {t}: {actual} != {expected}")
    jumps = [row["t"] for row in rows if row["jump"]]
    comparison_limit = min(limit, EXPECTED_JUMPS[-1])
    actual_prefix = [n for n in jumps if n <= comparison_limit]
    expected_prefix = [n for n in EXPECTED_JUMPS if n <= comparison_limit]
    lower = sum((Fraction(1, 3*n) for n in jumps), Fraction())
    # Sum over ALL smooth reciprocals is (1-1/2)^-1 (1-1/3)^-1 = 3.
    # Every missing jump term is nonnegative and at most its smooth term.
    tail_bound = 1 - sum((Fraction(1, 3*row["t"]) for row in rows), Fraction())
    upper = lower + tail_bound
    difference = {
        "lower": fraction_record(lower - EXPECTED_DENSITY),
        "upper": fraction_record(upper - EXPECTED_DENSITY),
    }
    return {
        "method": "Boolean hitting set; exact MaxSAT with closed integer bounds; no column DP",
        "z3_version": z3.get_version_string(),
        "limit": limit,
        "smooth_count": len(rows),
        "g_at_limit": g_from_rows(rows, limit),
        "jump_count": len(jumps),
        "jumps": jumps,
        "prefix_comparison": {
            "through": comparison_limit,
            "expected": expected_prefix,
            "actual": actual_prefix,
            "agree": actual_prefix == expected_prefix,
        },
        "brute_force_all_integer_cutoffs_through": brute_limit,
        "density_lower": fraction_record(lower),
        "density_upper": fraction_record(upper),
        "density_tail_bound": fraction_record(tail_bound),
        "requested_decimal": "0.8009657549",
        "requested_decimal_in_interval": lower <= EXPECTED_DENSITY <= upper,
        "difference_from_requested_decimal": difference,
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=10**11)
    parser.add_argument("--brute-limit", type=int, default=64)
    parser.add_argument("--timeout-ms", type=int, default=0,
                        help="per-query time limit; UNKNOWN is an error")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--progress", action="store_true")
    args = parser.parse_args()
    if min(args.limit, args.brute_limit, args.timeout_ms) < 0:
        parser.error("limits must be nonnegative")
    rows = exact_prefix(args.limit, args.timeout_ms, args.progress)
    report = make_report(args.limit, rows, args.brute_limit)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    summary = {key: value for key, value in report.items() if key not in ("rows", "jumps")}
    print(json.dumps(summary, indent=2))
    if not report["prefix_comparison"]["agree"]:
        raise SystemExit("DISAGREEMENT with the requested jump prefix")


if __name__ == "__main__":
    main()
