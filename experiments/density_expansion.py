#!/usr/bin/env python3
"""Exact density regroupings of the frozen rule, not new solver results.

All cutoffs, ratios, contributions, coefficients and error bounds use
integer arithmetic or Fraction. Decimal values are only displays.
"""

import argparse
import csv
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
from math import lcm
from pathlib import Path

from candidate_formula import compare, lattice_points, saved_report


def record(value):
    value = Fraction(value)
    with localcontext() as context:
        context.prec = 80
        decimal = str(Decimal(value.numerator) / Decimal(value.denominator))
    return {"fraction": str(value), "numerator": value.numerator,
            "denominator": value.denominator, "decimal": decimal}


def source(path):
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def below(n, base):
    exponent, power = 0, 1
    while power*base <= n:
        exponent, power = exponent+1, power*base
    return exponent, power


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def scan(limit, saved_counts, saved_g, keep_through):
    """Compute birth increments without calling the old prediction code."""
    counts = [0, 0, 0]
    h, E, g = 0, 0, 0
    H, W, reciprocal_sum, jump_sum = (Fraction(0) for _ in range(4))
    increments, window_flux, events, rows = {}, {}, [], []
    largest_spread, episode_counts = 0, {}
    matched = 0
    for t, a, b in lattice_points(limit):
        old_counts = counts.copy()
        births = [0, 0, 0]
        if b == 1:
            births[(a-1) % 3] += 1
            births[(a+1) % 3] += 1
            if a == 0:
                births[0] += 1
        elif b >= 2:
            births[(a-b) % 3] += 1
        counts = [old+birth for old, birth in zip(counts, births)]
        next_h = min(counts)
        m = t.bit_length()-5
        inside = m >= 0 and 24*2**m <= t < 27*2**m
        next_E = int(inside and counts[(m+2) % 3] == next_h)
        dh, de = next_h-h, next_E-E
        jump = 1-dh+de
        if dh not in (0, 1) or jump not in (0, 1):
            raise AssertionError(f"increment bound fails at {t}")
        g += jump
        if t in saved_counts:
            if counts != saved_counts[t] or g != saved_g[t]:
                raise AssertionError(f"saved solver/count disagreement at {t}")
            matched += 1
        increments[a, b] = (dh, de, jump)
        H += Fraction(dh, t)
        W += Fraction(de, t)
        reciprocal_sum += Fraction(1, t)
        jump_sum += Fraction(jump, 3*t)
        largest_spread = max(largest_spread, max(counts)-min(counts))
        row = {"t": t, "a": a, "b": b, "birth_0": births[0],
               "birth_1": births[1], "birth_2": births[2],
               "c_0": counts[0], "c_1": counts[1], "c_2": counts[2],
               "h": next_h, "delta_h": dh, "E": next_E, "delta_E": de,
               "rule_jump": jump}
        if t <= keep_through:
            rows.append(row)
        if de:
            if m < 0:
                raise AssertionError("correction change outside a window")
            window_flux[m] = window_flux.get(m, Fraction(0))+Fraction(de, t)
            if de == 1:
                episode_counts[m] = episode_counts.get(m, 0)+1
            if t <= keep_through:
                events.append({**row, "m": m, "before_c_0": old_counts[0],
                               "before_c_1": old_counts[1], "before_c_2": old_counts[2]})
        h, E = next_h, next_E
    if matched != len(saved_counts):
        raise AssertionError("saved solver domain was not fully checked")
    if jump_sum != (reciprocal_sum-H+W)/3:
        raise AssertionError("direct and telescoping density sums disagree")
    return {
        "increments": increments, "window_flux": window_flux,
        "events": events, "rows": rows, "H": H, "W": W,
        "reciprocal_sum": reciprocal_sum, "jump_sum": jump_sum,
        "max_colour_spread": largest_spread, "episode_counts": episode_counts,
        "saved_exact_matches": matched,
    }


def coefficients(k, increments, window_flux):
    colour_numerator = window_numerator = 0
    for b in range(k+1):
        u = k-b
        even, odd = increments[2*u, b], increments[2*u+1, b]
        weight = 4**b * 3**u
        colour_numerator += (2*even[0]+odd[0])*weight
        window_numerator += (2*even[1]+odd[1])*weight
    colour = Fraction(colour_numerator, 4**k)
    correction = Fraction(window_numerator, 4**k)
    loss = colour-correction
    U = 4**k*(window_flux.get(2*k, Fraction(0))+window_flux.get(2*k+1, Fraction(0)))
    if not (0 <= colour <= 12 and 0 <= loss <= 12 and 0 <= U <= Fraction(1, 144)):
        raise AssertionError(f"coefficient bound fails at {k}")
    # A valid bounded-RATIONAL two-series formula has N=6, c=6,
    # alpha_k=2U_k and beta_k=-colour_k. These are not integer claims.
    alpha, beta = 2*U, -colour
    p = colour_numerator-window_numerator
    if k:
        A = (p*pow(3**k, -1, 4**k)) % (4**k)
        if A >= 4**k//2:
            A -= 4**k
    else:
        A = 0
    B = (p-A*3**k)//4**k
    if A*3**k+B*4**k != p:
        raise AssertionError("endpoint integer decomposition failed")
    # A different integer trial is exact only as paired finite summands.
    a_trial, b_trial = -A, -B
    if Fraction(a_trial, 4**k)+Fraction(b_trial, 3**k) != -loss/3**k:
        raise AssertionError("paired coefficient equality failed")
    j, p3 = below(4**k, 3)
    i, p4 = below(3**k, 4)
    return {
        "k": k, "floor_log3_4k": j, "floor_log4_3k": i,
        "ratio4": record(Fraction(4**k, p3)), "ratio3": record(Fraction(3**k, p4)),
        "alpha_rational": record(alpha), "beta_rational": record(beta),
        "colour_diagonal": record(colour), "window_diagonal": record(correction),
        "loss_diagonal": record(loss), "window_U": record(U),
        "integer_trial_a": a_trial, "integer_trial_b": b_trial,
        "trial_a_normalized": record(Fraction(a_trial, 4**k)),
        "trial_b_normalized": record(Fraction(b_trial, 3**k)),
    }


def ratio_bands(rows, ratio_key, coefficient_key, thresholds, through):
    """Reject a proposed small band catalog by exact same-band conflicts."""
    representatives, conflicts = {}, []
    sample = [r for r in rows if r["k"] <= through]
    for row in sample:
        ratio = Fraction(row[ratio_key]["fraction"])
        band = next(i for i in range(len(thresholds)-1)
                    if thresholds[i] <= ratio < thresholds[i+1])
        value = row[coefficient_key]["fraction"]
        if band not in representatives:
            representatives[band] = row
        elif value != representatives[band][coefficient_key]["fraction"]:
            conflicts.append({"k": row["k"], "band": band,
                              "ratio": str(ratio), "coefficient": value,
                              "representative_k": representatives[band]["k"],
                              "representative_coefficient": representatives[band][coefficient_key]["fraction"]})
    ordered = sorted(sample, key=lambda r: Fraction(r[ratio_key]["fraction"]))
    necessary_intervals = 1+sum(
        left[coefficient_key]["fraction"] != right[coefficient_key]["fraction"]
        for left, right in zip(ordered, ordered[1:])
    )
    return {"through": through, "thresholds": list(map(str, thresholds)),
            "conflicts": conflicts, "conflict_count": len(conflicts),
            "minimum_intervals_to_fit_this_finite_sample": necessary_intervals,
            "interpretation": "Rejects only this catalog; finite samples cannot rule out every possible interval formula."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--through", type=int, default=40)
    parser.add_argument("--audit-through", type=int, default=160)
    parser.add_argument("--exact", type=Path, default=Path("experiments/results-1e14.json"))
    parser.add_argument("--output", type=Path, default=Path("experiments/density-expansion.json"))
    args = parser.parse_args()
    if not 0 <= args.through <= args.audit_through:
        raise ValueError("need 0 <= through <= audit-through")
    frozen_path = Path("experiments/predicted-1e14.json")
    frozen = json.loads(frozen_path.read_text())
    rule_source = source(Path("experiments/excess_rule.py"))
    if rule_source["sha256"] != frozen["rule_source_sha256"]:
        raise AssertionError("frozen rule changed")
    saved, saved_points, exact_source = saved_report(args.exact)
    compared = compare(saved, saved_points)
    saved_counts = {r["t"]: [r[f"c_{j}"] for j in range(3)] for r in compared}
    saved_g = {r["t"]: r["exact_g"] for r in compared}
    keep_limit, limit = 54*4**args.through, 54*4**args.audit_through
    scanned = scan(limit, saved_counts, saved_g, keep_limit)
    coeffs = [coefficients(k, scanned["increments"], scanned["window_flux"])
              for k in range(args.audit_through+1)]
    wanted = coeffs[:args.through+1]
    partial = Fraction(1)
    paired_partial = Fraction(1)
    for row in wanted:
        k = row["k"]
        partial += (Fraction(row["alpha_rational"]["fraction"])/4**k
                    + Fraction(row["beta_rational"]["fraction"])/3**k)/6
        paired_partial += (Fraction(row["integer_trial_a"], 4**k)
                           + Fraction(row["integer_trial_b"], 3**k))/6
    # Correct signed tails: omitted colour terms are nonpositive;
    # omitted completed-window terms are nonnegative.
    lower = partial-Fraction(1, 3**args.through)
    upper = partial+Fraction(1, 1296*4**args.through)
    paired_lower = paired_partial-Fraction(1, 3**args.through)
    paired_upper = paired_partial
    smooth_lower = scanned["jump_sum"]
    smooth_upper = smooth_lower+(3-scanned["reciprocal_sum"])/3
    if max(lower, paired_lower, smooth_lower) > min(upper, paired_upper, smooth_upper):
        raise AssertionError("independent exact truncation intervals are disjoint")
    true_lower = sum((Fraction(r["jump"], 3*r["t"]) for r in saved["rows"]), Fraction(0))
    true_upper = true_lower+(3-sum((Fraction(1, r["t"]) for r in saved["rows"]), Fraction(0)))/3
    catalog4 = list(map(Fraction, ("1", "9/8", "3/2", "27/16", "3")))
    catalog3 = list(map(Fraction, ("1", "3/2", "27/16", "3", "27/8", "4")))
    scale = lcm(*((Fraction(r[key]["fraction"])/6).denominator
                  for r in wanted for key in ("alpha_rational", "beta_rational")))
    scale_audit = lcm(*((Fraction(r[key]["fraction"])/6).denominator
                        for r in coeffs for key in ("alpha_rational", "beta_rational")))
    report = {
        "interpretation": "Conditional density of the frozen rule, not a proof of the rule for all t or of irrationality.",
        "rule_frozen_at_commit": frozen["rule_frozen_at_commit"], "rule_source": rule_source,
        "exact_source": exact_source, "saved_solver_matches": scanned["saved_exact_matches"],
        "coefficient_through": args.through, "audit_through": args.audit_through,
        "audit_smooth_limit": limit, "contributions_through": keep_limit,
        "bounded_rational_formula": "L_rule=(6+sum(alpha_k/4^k)+sum(beta_k/3^k))/6; alpha=2U, beta=-C_H",
        "rational_coefficient_bounds": {"alpha": "0 <= alpha <= 1/72", "beta": "-12 <= beta <= 0"},
        "partial_rational_series": record(partial),
        "rational_series_lower": record(lower), "rational_series_upper": record(upper),
        "partial_paired_integer_series": record(paired_partial),
        "paired_series_lower": record(paired_lower), "paired_series_upper": record(paired_upper),
        "direct_smooth_lower": record(smooth_lower), "direct_smooth_upper": record(smooth_upper),
        "direct_colour_sum_H": record(scanned["H"]), "direct_window_sum_W": record(scanned["W"]),
        "actual_density_lower_from_saved_solver": record(true_lower),
        "actual_density_upper_from_saved_solver": record(true_upper),
        "minimum_common_integer_N_for_natural_coefficients_through_K": scale,
        "minimum_common_integer_N_through_audit": scale_audit,
        "largest_integer_trial_abs_a_through_K": max(abs(r["integer_trial_a"]) for r in wanted),
        "largest_integer_trial_abs_b_through_K": max(abs(r["integer_trial_b"]) for r in wanted),
        "largest_integer_trial_abs_a_through_audit": max(abs(r["integer_trial_a"]) for r in coeffs),
        "largest_integer_trial_abs_b_through_audit": max(abs(r["integer_trial_b"]) for r in coeffs),
        "ratio_band_checks": {
            "alpha_40": ratio_bands(coeffs, "ratio4", "alpha_rational", catalog4, args.through),
            "beta_40": ratio_bands(coeffs, "ratio3", "beta_rational", catalog3, args.through),
            "alpha_audit": ratio_bands(coeffs, "ratio4", "alpha_rational", catalog4, args.audit_through),
            "beta_audit": ratio_bands(coeffs, "ratio3", "beta_rational", catalog3, args.audit_through),
        },
        "max_colour_spread_in_audit": scanned["max_colour_spread"],
        "multiple_positive_episodes": {str(m): count for m, count in scanned["episode_counts"].items() if count > 1},
        "integer_trial_interpretation": "Exact paired finite summands; no boundedness or convergence of the separate integer-coefficient series is asserted.",
        "requested_integer_ratio_only_formula_established": False,
        "coefficients": wanted,
    }
    args.output.write_text(json.dumps(report, indent=2)+"\n")
    flat = [{"k": r["k"], "ratio4": r["ratio4"]["fraction"],
             "ratio3": r["ratio3"]["fraction"],
             "alpha_rational": r["alpha_rational"]["fraction"],
             "beta_rational": r["beta_rational"]["fraction"],
             "colour_diagonal": r["colour_diagonal"]["fraction"],
             "window_U": r["window_U"]["fraction"],
             "integer_trial_a": r["integer_trial_a"], "integer_trial_b": r["integer_trial_b"]}
            for r in wanted]
    write_csv(args.output.with_suffix(".csv"), flat)
    write_csv(args.output.with_name("density-contributions.csv"), scanned["rows"])
    write_csv(args.output.with_name("density-window-events.csv"), scanned["events"])
    print(json.dumps({key: report[key] for key in (
        "saved_solver_matches", "coefficient_through", "audit_through", "partial_rational_series",
        "rational_series_lower", "rational_series_upper", "partial_paired_integer_series",
        "direct_smooth_lower", "largest_integer_trial_abs_a_through_K",
        "largest_integer_trial_abs_b_through_K",
        "minimum_common_integer_N_for_natural_coefficients_through_K",
        "requested_integer_ratio_only_formula_established")}, indent=2))


if __name__ == "__main__":
    main()
