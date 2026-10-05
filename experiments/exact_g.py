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


class CoverSolver:
    """One fixed prefix, with optional point constraints as assumptions.

    The prefix has its own Z3 context. Constrained queries reuse this
    fixed formula without adding vertices, clauses, or soft objectives.
    Assumptions are local to one check and never survive into the next.
    """

    def __init__(self, weights, triples, timeout_ms=0, engine="rc2"):
        self.weights, self.triples = list(weights), list(triples)
        self.context = z3.Context()
        self.variables = {
            n: z3.Bool(str(n), ctx=self.context) for n in self.weights
        }
        self.solver = z3.Optimize(ctx=self.context)
        self.solver.set(maxsat_engine=engine)
        if timeout_ms:
            self.solver.set(timeout=timeout_ms)
        self.solver.add(*(
            z3.Or(*(self.variables[n] for n in triple))
            for triple in self.triples
        ))
        handles = [
            self.solver.add_soft(z3.Not(variable), weight=1)
            for variable in self.variables.values()
        ]
        # Same default objective id and unit weights: one cost per omission.
        self.objective = handles[0]

    def solve(self, *, excluded=None, required=None):
        """Return the exact minimum omissions and a checked witness."""
        assumptions = []
        if excluded is not None:
            assumptions.append(self.variables[excluded])
        if required is not None:
            assumptions.append(z3.Not(self.variables[required]))
        result = self.solver.check(*assumptions)
        if result != z3.sat:
            raise RuntimeError(
                f"no exact result at t={self.weights[-1]}, "
                f"excluded={excluded}, required={required}: "
                f"{result}; {self.solver.reason_unknown()}"
            )
        lower = self.solver.lower(self.objective)
        upper = self.solver.upper(self.objective)
        if not (z3.is_int_value(lower) and z3.is_int_value(upper)
                and lower.as_long() == upper.as_long()):
            raise RuntimeError(f"unclosed objective: {lower}, {upper}")
        model = self.solver.model()
        cover = {
            n for n, variable in self.variables.items()
            if z3.is_true(model.eval(variable, model_completion=True))
        }
        checked_cover(self.weights, cover, self.triples)
        if len(cover) != lower.as_long():
            raise AssertionError("incorrect witness cardinality")
        if excluded is not None and excluded not in cover:
            raise AssertionError("witness violates exclusion")
        if required is not None and required in cover:
            raise AssertionError("witness violates requirement")
        return lower.as_long(), cover


def minimum_cover(weights, triples, timeout_ms=0, engine="rc2"):
    """Solve one prefix in a fresh solver AND a fresh Z3 context."""
    return CoverSolver(weights, triples, timeout_ms, engine).solve()


def exact_prefix(limit, timeout_ms=0, progress=False, engine="rc2", checkpoint=None):
    """Compute g at every smooth point up to limit, with cover witnesses.

    Corner clauses are hard constraints; each non-omitted vertex is a
    unit-weight soft constraint. The exact minimum soft cost is the
    minimum number of omissions. Check matching integer lower and upper
    bounds and the returned cover; UNKNOWN aborts the computation.
    """
    positions, weights, triples = {}, [], []
    minimum, rows = 0, []
    for weight, a, b in smooth_points(limit):
        started = time.perf_counter()
        positions[a, b] = len(weights)
        weights.append(weight)
        # Any corner containing the new point has one of these anchors.
        for x, y in ((a, b), (a - 1, b), (a, b - 1)):
            corner = ((x, y), (x + 1, y), (x, y + 1))
            if all(point in positions for point in corner):
                indices = [positions[point] for point in corner]
                triples.append(tuple(weights[i] for i in indices))
        previous_minimum = minimum
        minimum, cover = minimum_cover(weights, triples, timeout_ms, engine)
        if minimum not in (previous_minimum, previous_minimum + 1):
            raise AssertionError("minimum cover violates one-point bound")
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
            "minimum_cover_upper": minimum,
            "seconds": round(time.perf_counter() - started, 6),
        }
        rows.append(row)
        if checkpoint is not None:
            checkpoint.write(json.dumps(row) + "\n")
            checkpoint.flush()
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


def make_report(limit, rows, brute_limit, engine="rc2"):
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
    report = {
        "method": "Boolean hitting set; exact MaxSAT with closed integer bounds; no column DP",
        "maxsat_engine": engine,
        "optimization_state": "fresh solver and Z3 context at each prefix; hard clauses before soft clauses",
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
    scale = 10**10
    shifted = lower * scale + Fraction(1, 2)
    rounded_units = shifted.numerator // shifted.denominator
    # Strictly inside one rounding cell: no tie convention is needed.
    if (Fraction(2*rounded_units - 1, 2*scale) < lower
            and upper < Fraction(2*rounded_units + 1, 2*scale)):
        report["certified_rounding_decimal_places"] = 10
        report["certified_rounded_density"] = (
            f"{rounded_units // scale}.{rounded_units % scale:010d}"
        )
    else:
        report["certified_rounding_decimal_places"] = None
        report["certified_rounded_density"] = None
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=10**11)
    parser.add_argument("--brute-limit", type=int, default=64)
    parser.add_argument("--timeout-ms", type=int, default=0,
                        help="per-query time limit; UNKNOWN is an error")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--engine", choices=("rc2", "maxres"), default="rc2")
    parser.add_argument("--progress", action="store_true")
    args = parser.parse_args()
    if min(args.limit, args.brute_limit, args.timeout_ms) < 0:
        parser.error("limits must be nonnegative")
    if args.output:
        # Preserve every completed query even if a later query times out.
        # The partial file is diagnostic data, never an optimization input.
        with args.output.with_suffix(".partial.jsonl").open("w") as checkpoint:
            rows = exact_prefix(args.limit, args.timeout_ms, args.progress,
                                args.engine, checkpoint)
    else:
        rows = exact_prefix(args.limit, args.timeout_ms, args.progress, args.engine)
    report = make_report(args.limit, rows, args.brute_limit, args.engine)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    summary = {key: value for key, value in report.items() if key not in ("rows", "jumps")}
    print(json.dumps(summary, indent=2))
    if not report["prefix_comparison"]["agree"]:
        raise SystemExit("DISAGREEMENT with the requested jump prefix")


if __name__ == "__main__":
    main()
