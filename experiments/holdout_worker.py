#!/usr/bin/env python3
"""One unrestricted exact MaxSAT query, isolated from predictions."""

import argparse
import json
from pathlib import Path
import resource
import time

from exact_g import CoverSolver, smooth_points


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("t", type=int)
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--memory-mib", type=int, default=1024)
    parser.add_argument("--engine", choices=("rc2", "maxres"), default="rc2")
    args = parser.parse_args()
    if args.memory_mib:
        cap = args.memory_mib * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    started = time.perf_counter()
    points = smooth_points(args.t)
    weights = [n for n, _, _ in points]
    domain = set(weights)
    triples = [(n, 2*n, 3*n) for n in weights if 3*n in domain]
    result = {"t": args.t, "points": len(weights), "engine": args.engine,
              "timeout_ms": args.timeout_ms, "address_space_limit_mib": args.memory_mib}
    try:
        problem = CoverSolver(weights, triples, args.timeout_ms, args.engine)
        minimum, cover = problem.solve()
        result.update(status="exact", g=len(weights) - minimum,
                      minimum_cover_lower=minimum, minimum_cover_upper=minimum,
                      cover=sorted(cover))
    except (RuntimeError, MemoryError) as error:
        result.update(status="not_exact", error=str(error))
    result["seconds"] = round(time.perf_counter() - started, 6)
    result["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    process_status = Path("/proc/self/status").read_text().splitlines()
    result["proc_peak_rss_kib"] = int(next(line.split()[1] for line in process_status
                                         if line.startswith("VmHWM:")))
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
