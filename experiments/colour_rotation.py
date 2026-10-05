#!/usr/bin/env python3
"""Exact colour growth, coefficient partial sums, and rotation-coding tests.

Integer/Fraction arithmetic decides every count, phase order, interval
membership, and counterexample. Floating point is used only for exploratory
regressions, and Decimal logarithms only for human-readable coordinates.
No universal finite-interval impossibility is inferred from finite samples.
"""

import argparse
from bisect import bisect_right
from decimal import Decimal, localcontext
from fractions import Fraction
import json
from math import log, sqrt
from pathlib import Path

from candidate_formula import lattice_points
from colour_imbalance import birth, row_colours, row_formula
from density_expansion import record, source, write_csv


def minima(counts):
    return tuple(j for j, c in enumerate(counts) if c == min(counts))


def mask(counts):
    return sum(1 << j for j in minima(counts))


def location(t, a, b, counts, k):
    u, v = counts[0]-counts[1], counts[1]-counts[2]
    with localcontext() as context:
        context.prec = 50
        x = str(Decimal(t).ln()/Decimal(2).ln())
    return {"t": t, "a": a, "b": b, "floor_log3_t": k,
            "full_row_triples_after_boundary": max(0, (k-1)//3),
            "x_log2_t_display": x, "counts": counts.copy(), "D": [u, v],
            "d": sum(counts)-3*min(counts), "minimum_colours": minima(counts)}


def envelope(rows):
    return {"max_abs_D0": max(abs(r["D0"]) for r in rows),
            "max_abs_D1": max(abs(r["D1"]) for r in rows),
            "max_D_infinity": max(max(abs(r["D0"]), abs(r["D1"])) for r in rows),
            "max_D_euclidean_squared": max(r["D0"]**2+r["D1"]**2 for r in rows),
            "max_spread": max(r["spread"] for r in rows),
            "max_d": max(r["d"] for r in rows)}


def smooth_scan(through):
    limit = 54*4**through
    power3s = [1]
    while power3s[-1]*3 <= limit:
        power3s.append(power3s[-1]*3)
    counts, oldd, coefficients, rows, records = [0, 0, 0], 0, {}, [], []
    metrics = {name: 0 for name in ("D_infinity", "abs_D0", "abs_D1", "spread", "d")}
    for t, a, b in lattice_points(limit):
        birth(t, a, b, counts)
        u, v = counts[0]-counts[1], counts[1]-counts[2]
        d = sum(counts)-3*min(counts)
        k = bisect_right(power3s, t)-1
        coefficients[k] = coefficients.get(k, Fraction(0))+Fraction((d-oldd)*power3s[k], t)
        values = {"D_infinity": max(abs(u), abs(v)), "abs_D0": abs(u),
                  "abs_D1": abs(v), "spread": max(counts)-min(counts), "d": d}
        changed = [name for name in metrics if values[name] > metrics[name]]
        if changed:
            records.append({**location(t, a, b, counts, k),
                            "new_records": {name: values[name] for name in changed}})
        metrics = {name: max(metrics[name], values[name]) for name in metrics}
        rows.append({"t": t, "a": a, "b": b, "k": k,
                     "c_0": counts[0], "c_1": counts[1], "c_2": counts[2],
                     "D0": u, "D1": v, "spread": values["spread"], "d": d,
                     "delta_d": d-oldd, "minimum_mask": mask(counts)})
        oldd = d
    B_rows, partial, weighted = [], Fraction(0), Fraction(0)
    for k, B in sorted(coefficients.items()):
        partial += B
        weighted += B/power3s[k]
        B_rows.append({"k": k, "complete": int(3**(k+1) <= limit),
                       "b_k": str(B), "b_k_display": float(B),
                       "sum_b_0_to_k": str(partial), "sum_b_display": float(partial),
                       "sum_b_over_3k": str(weighted), "sum_weighted_display": float(weighted)})
    checkpoints = []
    for K in sorted({0, 5, 10, 20, 40, 80, 120, through}):
        if K > through:
            continue
        sample = [r for r in rows if r["t"] <= 54*4**K]
        checkpoints.append({"K": K, "limit": 54*4**K, "smooth_count": len(sample),
                            **envelope(sample)})
    maxima = {}
    for name in metrics:
        def value(row):
            if name == "D_infinity":
                return max(abs(row["D0"]), abs(row["D1"]))
            if name.startswith("abs_D"):
                return abs(row[name[4:]])
            return row[name]
        hits = [r for r in rows if value(r) == metrics[name]]
        maxima[name] = {"value": metrics[name], "occurrences": len(hits),
                        "first": hits[0], "last": hits[-1]}
    max_B = max(coefficients, key=lambda k: abs(coefficients[k]))
    complete_B = B_rows[:-1] if not B_rows[-1]["complete"] else B_rows
    partial_records = []
    high, low = Fraction(0), Fraction(0)
    for r in B_rows:
        s = Fraction(r["sum_b_0_to_k"])
        if s > high or s < low:
            partial_records.append({"k": r["k"], "sum_b": record(s), "complete": r["complete"]})
            high, low = max(high, s), min(low, s)
    extrema_rows = {name: extreme(B_rows, key=lambda r: Fraction(r["sum_b_0_to_k"]))
                    for name, extreme in (("minimum", min), ("maximum", max))}
    summary = {"limit": limit, "smooth_count": len(rows), "maxima": maxima,
               "records": records, "checkpoints": checkpoints,
               "largest_abs_b": {"k": max_B, "b": record(coefficients[max_B])},
               "last_complete_block": complete_B[-1], "last_truncated_block": B_rows[-1],
               "unweighted_partial_sum_extrema": extrema_rows,
               "partial_sum_records": partial_records,
               "selected_partials": [r for r in B_rows if r["k"] in {0, 20, 40, 80, 120, 160, 204, 205}]}
    return summary, rows, B_rows


def powers_of_three(through):
    # Normalizing colours by adding k turns row b into n=k-b. Its
    # contribution is Q(floor(n theta)+1,-n), independent of k.
    S, power3, word_counts = [0, 0, 0], 1, [0, 0, 0]
    rows = [{"k": 0, "c_0": 0, "c_1": 0, "c_2": 0, "D0": 0, "D1": 0,
             "spread": 0, "d": 0, "minimum_mask": 7, "least_minimum": 0,
             "normalised_minimum_mask": 7, "floor_k_theta": 0}]
    phases = {"k_theta": [Fraction(1)], "k_theta_over_3": [Fraction(1)],
              "k_theta_plus_1_over_3": [Fraction(1)]}
    for k in range(1, through+1):
        n, N = k-1, power3.bit_length()
        residue = row_colours(N, -n)
        S = [c+r for c, r in zip(S, residue)]
        r0 = row_colours(N+1, 0)
        counts = [S[(j+k) % 3]+r0[j] for j in range(3)]
        # Exact verification of the complex identity in Z[z]/(1+z+z^2).
        word_counts[(N-1+n) % 3] += 1
        A, B = S[0]-S[2], S[1]-S[2]
        W0, W1 = word_counts[0]-word_counts[2], word_counts[1]-word_counts[2]
        cyclic = row_colours(k, 0)  # sum_{n<k} z^n
        V0, V1 = cyclic[0]-cyclic[2], cyclic[1]-cyclic[2]
        if (A+B, 2*B-A) != (V0+W1, V1-W0+W1):
            raise AssertionError(f"rotation-word identity fails at k={k}")
        power3 *= 3
        if k <= 205 or k in {306, 665, 918, 1995, through}:
            if counts != row_formula(power3)[0]:
                raise AssertionError(f"pure-power recurrence fails at k={k}")
        row = {"k": k, **{f"c_{j}": counts[j] for j in range(3)},
               "D0": counts[0]-counts[1], "D1": counts[1]-counts[2],
               "spread": max(counts)-min(counts), "d": sum(counts)-3*min(counts),
               "minimum_mask": mask(counts), "least_minimum": min(minima(counts)),
               "normalised_minimum_mask": sum(1 << ((j+k) % 3) for j in minima(counts)),
               "floor_k_theta": power3.bit_length()-1}
        rows.append(row)
        # These positive ratios are monotone functions of the requested
        # circle phases, so Fraction comparisons order phases exactly.
        exponent = power3.bit_length()-1
        phases["k_theta"].append(Fraction(power3, 2**exponent))
        phases["k_theta_over_3"].append(Fraction(power3, 8**(exponent//3)))
        power6 = power3*2**k
        phases["k_theta_plus_1_over_3"].append(Fraction(power6, 8**((power6.bit_length()-1)//3)))
    checkpoints = []
    for K in (205, 306, 665, 1024, 1995, 4096, 8192):
        if K <= through:
            checkpoints.append({"through_k": K, **envelope(rows[:K+1])})
    records, oldD, oldd = [], 0, 0
    for r in rows:
        D = max(abs(r["D0"]), abs(r["D1"]))
        if D > oldD or r["d"] > oldd:
            records.append(r)
            oldD, oldd = max(oldD, D), max(oldd, r["d"])
    max_d = max(r["d"] for r in rows)
    max_D = max(max(abs(r["D0"]), abs(r["D1"])) for r in rows)
    return {"through_k": through, "checkpoints": checkpoints, "records": records,
            "maximum_d_first_k": next(r["k"] for r in rows if r["d"] == max_d),
            "maximum_D_first_k": next(r["k"] for r in rows if max(abs(r["D0"]), abs(r["D1"])) == max_D),
            "cf_denominator_cutoffs": [rows[q] for q in (1, 2, 5, 12, 41, 53, 306, 665, 1995) if q <= through],
            "exact_complex_identity_checks": through}, rows, phases


def interval_complexity(rows, phases, label):
    ordered = sorted(range(len(rows)), key=lambda i: phases[i])
    return 1+sum(rows[i][label] != rows[j][label] for i, j in zip(ordered, ordered[1:]))


def band_conflict(rows, phase, edges, label="minimum_mask", start=1):
    seen = {}
    for i in range(start, len(rows)):
        band = bisect_right(edges, phase[i])-1
        key = band
        if key in seen and rows[i][label] != rows[seen[key]][label]:
            old = seen[key]
            return {"first_k": old, "conflicting_k": i, "band": band,
                    "first_label": rows[old][label], "conflicting_label": rows[i][label],
                    "first_ratio": str(phase[old]), "conflicting_ratio": str(phase[i])}
        seen.setdefault(key, i)
    return None


def fitted_intervals(rows, phase, train_through=40):
    ordered = sorted(range(1, train_through+1), key=lambda i: phase[i])
    edges, labels = [], [rows[ordered[0]]["minimum_mask"]]
    for left, right in zip(ordered, ordered[1:]):
        if rows[left]["minimum_mask"] != rows[right]["minimum_mask"]:
            # Midpoint in the exact ratio coordinate, not an approximate log.
            edges.append((phase[left]+phase[right])/2)
            labels.append(rows[right]["minimum_mask"])
    for k in range(train_through+1, len(rows)):
        predicted = labels[bisect_right(edges, phase[k])]
        if predicted != rows[k]["minimum_mask"]:
            return {"train_k": [1, train_through], "fitted_intervals": len(labels),
                    "first_holdout_failure_k": k, "predicted_mask": predicted,
                    "actual_mask": rows[k]["minimum_mask"], "exact_ratio": str(phase[k])}
    return {"train_k": [1, train_through], "fitted_intervals": len(labels), "first_holdout_failure_k": None}


def balance_counterexample(rows, colour, start=1, max_length=32, use_least=False):
    values = [int(r["least_minimum"] == colour) if use_least else int(r["minimum_mask"] & (1 << colour) != 0) for r in rows]
    # Earliest prefix violating binary balance; all lengths up to 32.
    first = None
    for length in range(1, max_length+1):
        low = high = sum(values[start:start+length])
        low_at = high_at = start
        total = low
        for begin in range(start+1, len(values)-length+1):
            total += values[begin+length-1]-values[begin-1]
            if total-low >= 2 or high-total >= 2:
                other = low_at if total-low >= 2 else high_at
                result = {"length": length, "blocks_start_k": [other, begin],
                          "blocks": [values[other:other+length], values[begin:begin+length]],
                          "prefix_ends_k": begin+length-1}
                if first is None or result["prefix_ends_k"] < first["prefix_ends_k"]:
                    first = result
                break
            if total < low:
                low, low_at = total, begin
            if total > high:
                high, high_at = total, begin
    return first


def smooth_coding(rows):
    seen_phase, seen_phase_unique, seen_box, seen_box3, conflicts = {}, {}, {}, {}, {}
    powers3 = [1]
    for r in rows:
        t = r["t"]
        while powers3[-1]*3 <= t:
            powers3.append(powers3[-1]*3)
        if t < 3:
            continue
        ratio2 = Fraction(t, 2**(t.bit_length()-1))
        ratio3 = Fraction(t, powers3[-1])
        box = (bisect_right(list(map(Fraction, ("1", "9/8", "3/2", "27/16", "2"))), ratio2)-1,
               bisect_right(list(map(Fraction, ("1", "9/8", "3/2", "27/16", "2", "3"))), ratio3)-1)
        ratio8 = Fraction(t, 8**((t.bit_length()-1)//3))
        box3 = (bisect_right(list(map(Fraction, (1, 2, 4, 8))), ratio8)-1, box[1])
        for name, key, seen in (("same_fractional_x", ratio2, seen_phase),
                                ("geometric_two_phase_boxes", box, seen_box),
                                ("x_over_3_and_x_over_theta_boxes", box3, seen_box3)):
            if key in seen and seen[key]["minimum_mask"] != r["minimum_mask"] and name not in conflicts:
                conflicts[name] = {"first": seen[key], "conflict": r, "key": str(key)}
            seen.setdefault(key, r)
        if r["minimum_mask"] in (1, 2, 4):
            if ratio2 in seen_phase_unique and seen_phase_unique[ratio2]["minimum_mask"] != r["minimum_mask"] and "same_fractional_x_unique_minima" not in conflicts:
                conflicts["same_fractional_x_unique_minima"] = {"first": seen_phase_unique[ratio2], "conflict": r, "exact_ratio2": str(ratio2)}
            seen_phase_unique.setdefault(ratio2, r)
    return conflicts


def rational_cf(value):
    result = []
    while value.denominator != 1:
        a = value.numerator//value.denominator
        result.append(a)
        value = 1/(value-a)
    return result+[value.numerator]


def convergents():
    with localcontext() as context:
        context.prec = 100
        theta = Decimal(3).ln()/Decimal(2).ln()
        value, digits, candidates = theta, [], []
        p0, p1, q0, q1 = 0, 1, 1, 0
        while q1 < 30000:
            a = int(value)
            digits.append(a)
            p0, p1, q0, q1 = p1, a*p1+p0, q1, a*q1+q0
            candidates.append((p1, q1))
            value = 1/(value-a)
        bounds = sorted(Fraction(p, q) for p, q in candidates[-2:])
        low, high = bounds
        if not (3**low.denominator > 2**low.numerator and 3**high.denominator < 2**high.numerator):
            raise AssertionError("candidate theta bracket failed exact integer checks")
        left, right = rational_cf(low), rational_cf(high)
        common = 0
        while common < min(len(left), len(right)) and left[common] == right[common]:
            common += 1
        if digits[:common] != left[:common]:
            raise AssertionError("continued-fraction prefix differs from rational bracket")
        certified = []
        for p, q in candidates[:common]:
            certified.append({"p": p, "q": q, "p_plus_q_mod_3": (p+q) % 3,
                              "q_theta_minus_p_display": str(q*theta-p)})
    return {"certified_theta_bracket": list(map(str, bounds)),
            "certified_cf_digits": digits[:common], "convergents": certified}


def fit(samples, x_key, y_key):
    outputs = {}
    for name, transform in (("linear_log_t", lambda x: x),
                            ("sqrt_log_t", sqrt), ("log_log_t", log)):
        xs = [transform(float(s[x_key])) for s in samples]
        ys = [float(s[y_key]) for s in samples]
        xb, yb = sum(xs)/len(xs), sum(ys)/len(ys)
        slope = sum((x-xb)*(y-yb) for x, y in zip(xs, ys))/sum((x-xb)**2 for x in xs)
        intercept = yb-slope*xb
        error = sum((y-intercept-slope*x)**2 for x, y in zip(xs, ys))
        total = sum((y-yb)**2 for y in ys)
        outputs[name] = {"intercept": intercept, "slope": slope,
                         "R_squared": 1-error/total if total else None}
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--through", type=int, default=160)
    parser.add_argument("--powers-through", type=int, default=8192)
    args = parser.parse_args()
    smooth, smooth_rows, B_rows = smooth_scan(args.through)
    powers, power_rows, phases = powers_of_three(args.powers_through)
    coding = {"interpretation": "Rejects the stated finite catalogs and fits; growing interval counts do not disprove every eventual finite-interval coding.",
              "smooth_conflicts": smooth_coding(smooth_rows),
              "thirds_conflict_k_theta_over_3": band_conflict(power_rows, phases["k_theta_over_3"], list(map(Fraction, (1, 2, 4, 8)))),
              "thirds_conflict_alpha": band_conflict(power_rows, phases["k_theta_plus_1_over_3"], list(map(Fraction, (1, 2, 4, 8)))),
              "fitted_interval_holdouts": {key: fitted_intervals(power_rows, phase) for key, phase in phases.items()},
              "minimum_intervals": [],
              "binary_minimum_membership_balance_counterexamples": {str(j): balance_counterexample(power_rows, j) for j in range(3)},
              "least_minimum_binary_balance_counterexamples": {str(j): balance_counterexample(power_rows, j, use_least=True) for j in range(3)},
              "balance_counterexamples_after_startup": {str(start): {str(j): balance_counterexample(power_rows, j, start=start) for j in range(3)} for start in (8, 206, 1024)}}
    # For thirds of {k theta}, cube the normalized ratio to compare it
    # exactly with 2 and 4, avoiding algebraic/rounded interval endpoints.
    coding["thirds_conflict_k_theta"] = band_conflict(power_rows, [p**3 for p in phases["k_theta"]], list(map(Fraction, (1, 2, 4, 8))))
    for K in (40, 80, 160, 205, 665, 1995, 4096, 8192):
        if K > args.powers_through:
            continue
        coding["minimum_intervals"].append({"through_k": K, **{
            f"{phase}_{label}": interval_complexity(power_rows[1:K+1], values[1:K+1], label)
            for phase, values in phases.items()
            for label in ("minimum_mask", "least_minimum", "normalised_minimum_mask")}})
    cf = convergents()
    for r in smooth["records"]:
        Q = r["full_row_triples_after_boundary"]
        nearest = min(cf["convergents"], key=lambda c: abs(c["q"]-Q))
        r["closest_convergent_denominator_to_grouped_length"] = nearest["q"]
        r["grouped_length_minus_q"] = Q-nearest["q"]
    fit_samples = [{"x": 2*r["K"]+log(54, 2), "max_d": r["max_d"]} for r in smooth["checkpoints"] if r["K"] > 0]
    power_samples = [{"x": r["through_k"], "max_d": r["max_d"]} for r in powers["checkpoints"]]
    partial_samples = [{"x": r["k"], "sum": float(Fraction(r["sum_b_0_to_k"]))}
                       for r in B_rows if r["k"] > 0 and r["complete"]]
    report = {"interpretation": "Exact participating-colour data, with conditional frozen-rule density interpretation; regressions and coding extrapolations are exploratory.",
              "smooth": smooth, "powers_of_three": powers, "continued_fractions": cf, "coding": coding,
              "exploratory_fits_max_d": {"required_smooth_range": fit(fit_samples, "x", "max_d"),
                                          "extended_powers_of_three": fit(power_samples, "x", "max_d")},
              "exploratory_fits_unweighted_b_partials": fit(partial_samples, "x", "sum"),
              "program_source": source(Path(__file__)), "row_program_source": source(Path("experiments/colour_imbalance.py")),
              "verification_source": source(Path("experiments/colour-imbalance-verification.json"))}
    Path("experiments/colour-rotation.json").write_text(json.dumps(report, indent=2)+"\n")
    write_csv(Path("experiments/colour-imbalance-cutoffs.csv"), smooth_rows)
    write_csv(Path("experiments/colour-imbalance-coefficients.csv"), B_rows)
    write_csv(Path("experiments/colour-imbalance-powers3.csv"), power_rows)
    print(json.dumps({"smooth": smooth["checkpoints"], "max_b": smooth["largest_abs_b"],
                      "last_complete_block": smooth["last_complete_block"], "last_truncated_block": smooth["last_truncated_block"],
                      "powers3": powers["checkpoints"], "coding": coding,
                      "cf": cf, "fits": report["exploratory_fits_max_d"]}, indent=2))


if __name__ == "__main__":
    main()
