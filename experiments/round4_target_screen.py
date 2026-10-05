#!/usr/bin/env python3
"""Bounded exact-integer screening; this script produces no Lean proofs.

Each run has its own wall-time cap. JSON records completed bounds explicitly.
"""
import argparse
import functools
import itertools
import json
import math
import time
from pathlib import Path


def run(kind, seconds):
    start = time.monotonic()
    deadline = start + seconds
    result = {"experiment": kind, "time_cap_seconds": seconds,
              "arithmetic": "Python exact integers", "witnesses": []}

    def expired():
        return time.monotonic() >= deadline

    if kind in ("686-four", "686-twenty-five"):
        ratio = 4 if kind == "686-four" else 25
        limit = 100000
        completed = []
        for k in range(2, 65):
            # P(t,k) is strictly increasing in t >= 0. A dictionary gives
            # an exhaustive match test over both starts <= limit.
            values = {}
            product = math.factorial(k)
            last_n = -1
            for n in range(limit + 1):
                if n % 1024 == 0 and expired():
                    break
                values[product] = n
                product = product // (n + 1) * (n + k + 1)
                last_n = n
            product = math.factorial(k)
            checked_n = -1
            for n in range(last_n + 1):
                if n % 1024 == 0 and expired():
                    break
                m = values.get(ratio * product)
                if m is not None and m >= n + k:
                    result["witnesses"].append({"k": k, "n": n, "m": m})
                product = product // (n + 1) * (n + k + 1)
                checked_n = n
            if last_n == limit and checked_n == limit:
                completed.append(k)
            else:
                result["partial_k"] = {"k": k, "m_max": last_n,
                                       "n_max": checked_n}
                break
        result.update({"ratio": ratio, "start_bound": limit,
                       "completed_k": completed})
        # Independent sanity checks of the exact equation, not target wins.
        result["known_witness_checks"] = [
            {"ratio": r, "k": k, "n": n, "m": m,
             "valid": math.prod(range(m + 1, m + k + 1)) ==
                      r * math.prod(range(n + 1, n + k + 1))}
            for r, k, n, m in [(9, 3, 11, 25), (16, 3, 4, 13)]]
    elif kind == "677":
        limit = 20000
        completed = []
        for k in range(1, 65):
            first = {}
            last_n = -1
            for n in range(limit + 1):
                if n % 128 == 0 and expired():
                    break
                value = math.lcm(*range(n + 1, n + k + 1))
                old = first.setdefault(value, n)
                if n >= old + k:
                    result["witnesses"].append({"k": k, "n": old, "m": n,
                                                "lcm": str(value)})
                last_n = n
            if last_n == limit:
                completed.append(k)
            else:
                result["partial_k"] = {"k": k, "start_max": last_n}
                break
        result.update({"start_bound": limit, "completed_k": completed,
                       "unequal_length_sanity": math.lcm(5, 6, 7) == math.lcm(14, 15)})
    elif kind == "406-one-two":
        limit = 100000
        hits = []
        checked = -1
        for exponent in range(limit + 1):
            if exponent % 128 == 0 and expired():
                break
            value = 1 << exponent
            while value:
                value, digit = divmod(value, 3)
                if digit == 0:
                    break
            else:
                hits.append(exponent)
                if exponent > 15:
                    result["witnesses"].append({"exponent": exponent})
            checked = exponent
        result.update({"exponent_max_completed": checked,
                       "all_admissible_exponents_in_range": hits})
    elif kind == "699":
        limit = 300
        primes = [p for p in range(2, limit + 1)
                  if all(p % d for d in range(2, math.isqrt(p) + 1))]

        @functools.lru_cache(maxsize=200000)
        def greatest_prime_factor(value):
            # A binomial coefficient C(n,i), n <= limit, has no prime
            # factor above limit. Descending trial division is complete.
            if value == 1:
                return 1
            return next(p for p in reversed(primes) if value % p == 0)

        strong = []
        pairs = 0
        completed = 0
        for n in range(1, limit + 1):
            row = [math.comb(n, i) for i in range(n // 2 + 1)]
            done = True
            for i in range(1, n // 2):
                if expired():
                    done = False
                    break
                for j in range(i + 1, n // 2 + 1):
                    factor = greatest_prime_factor(math.gcd(row[i], row[j]))
                    pairs += 1
                    if factor < i:
                        result["witnesses"].append({"n": n, "i": i, "j": j})
                    if factor <= i:
                        strong.append([n, i, j])
            if not done:
                result["partial_n"] = n
                break
            completed = n
        result.update({"n_max_completed": completed, "pairs_checked": pairs,
                       "strong_form_exceptions": strong,
                       "known_gcd_28_5_14": math.gcd(math.comb(28, 5), math.comb(28, 14))})
    elif kind == "128-circulant":
        # Only circulant graphs are screened. For the formal premise,
        # it is enough to check all floor(n/2)-sets: larger sets contain
        # such a set, and induced edge count is monotone.
        counts = {"generator_sets": 0, "triangle_free": 0,
                  "average_rejections": 0, "subsets_checked": 0}
        completed = 3
        for n in range(4, 25):
            done = True
            half = n // 2
            threshold = n * n // 50 + 1
            for generator_mask in range(1 << half):
                if expired():
                    done = False
                    break
                counts["generator_sets"] += 1
                distances = [d for d in range(1, half + 1)
                             if generator_mask >> (d - 1) & 1]
                steps = {d for d in distances} | {n - d for d in distances}
                if any((a + b) % n in steps for a in steps for b in steps):
                    continue
                counts["triangle_free"] += 1
                edge_count = n * len(steps) // 2
                if edge_count * half * (half - 1) < threshold * n * (n - 1):
                    counts["average_rejections"] += 1
                    continue
                adjacency = [sum(1 << ((v + d) % n) for d in steps)
                             for v in range(n)]
                minimum = edge_count
                exhausted = True
                for subset in itertools.combinations(range(n), half):
                    if counts["subsets_checked"] % 1024 == 0 and expired():
                        exhausted = False
                        done = False
                        break
                    counts["subsets_checked"] += 1
                    mask = sum(1 << v for v in subset)
                    edges = sum((adjacency[v] & mask).bit_count() for v in subset) // 2
                    minimum = min(minimum, edges)
                    if edges < threshold:
                        exhausted = False
                        break
                if exhausted:
                    result["witnesses"].append({"n": n, "distances": distances,
                                                "min_half_edges": minimum})
                if not done:
                    break
            if not done:
                result["partial_n"] = n
                break
            completed = n
        result.update({"n_max_completed": completed, "counts": counts,
                       "coverage": "all circulant graphs only, not all graphs"})
    elif kind == "373-maximal":
        facts = [math.factorial(n) for n in range(1001)]
        nodes = 0

        @functools.lru_cache(maxsize=200000)
        def decompose(q, bound):
            nonlocal nodes
            nodes += 1
            if nodes % 256 == 0 and expired():
                raise TimeoutError
            if q == 1:
                return ()
            if q & (q - 1) == 0:
                return (2,) * (q.bit_length() - 1)
            while bound >= 3 and facts[bound] > q:
                bound -= 1
            # Every remaining prime must be <= bound. Trial divisions by
            # ALL integers are unnecessary: gcd(q,bound!) catches support.
            remaining = q
            support = math.gcd(q, facts[bound])
            while support > 1:
                remaining //= support
                support = math.gcd(remaining, support)
            if remaining != 1:
                return None
            for a in range(bound, 2, -1):
                if q % facts[a] == 0:
                    tail = decompose(q // facts[a], a)
                    if tail is not None:
                        return (a,) + tail
            return None

        result["known_16_check"] = decompose(facts[16], 14)
        completed = 16
        for n in range(17, 1001):
            if expired():
                break
            try:
                parts = decompose(facts[n], n - 2)
            except TimeoutError:
                result["partial_n"] = n
                break
            if parts is not None:
                assert all(a > 1 for a in parts)
                assert all(a >= b for a, b in zip(parts, parts[1:]))
                assert parts[0] < n - 1
                assert math.prod(facts[a] for a in parts) == facts[n]
                result["witnesses"].append({"n": n, "parts": parts})
            completed = n
        result.update({"n_max_completed": completed, "recursive_nodes": nodes,
                       "cache": str(decompose.cache_info())})
    else:
        raise ValueError(kind)
    result["elapsed_seconds"] = round(time.monotonic() - start, 3)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=["686-four", "686-twenty-five", "677",
                                        "406-one-two", "373-maximal", "699",
                                        "128-circulant"])
    parser.add_argument("--seconds", type=float, default=90)
    args = parser.parse_args()
    output = run(args.kind, min(args.seconds, 600))
    path = Path("experiments") / ("round4-" + args.kind + ".json")
    path.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output))
