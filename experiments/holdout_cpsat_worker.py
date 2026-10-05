#!/usr/bin/env python3
"""One unrestricted corner-cover query using OR-Tools CP-SAT.

No fitted rule, predicted optimum, colour cover, or supplied bound enters
the model. OPTIMAL is required; FEASIBLE and UNKNOWN are not accepted.
"""

import argparse
import json
import os
from pathlib import Path
import resource
import time

# Keep numerical-library helper threads from inflating virtual memory.
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

import ortools
from ortools.sat.python import cp_model


def solve(t, timeout_ms, workers):
    weights = []
    power3 = 1
    while power3 <= t:
        weight = power3
        while weight <= t:
            weights.append(weight)
            weight *= 2
        power3 *= 3
    weights.sort()
    model = cp_model.CpModel()
    omitted = {n: model.new_bool_var(str(n)) for n in weights}
    for n in weights:
        if 3*n in omitted:
            model.add_bool_or([omitted[n], omitted[2*n], omitted[3*n]])
    objective = sum(omitted.values())
    model.minimize(objective)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout_ms / 1000
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 168
    status = solver.solve(model)
    result = {"points": len(weights), "solver_status": solver.status_name(status),
              "objective_bound": solver.best_objective_bound}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        cover = sorted(n for n in weights if solver.value(omitted[n]))
        minimum = solver.value(objective)
        # Numerical corner reconstruction, independent of model clauses.
        domain = set(weights)
        cover_set = set(cover)
        if len(cover) != minimum or not cover_set <= domain or any(
            not ({n, 2*n, 3*n} & cover_set) for n in weights if 3*n in domain
        ):
            raise AssertionError("invalid returned cover")
        result.update(feasible_g=len(weights)-minimum, feasible_cover=cover)
        if (status == cp_model.OPTIMAL
                and solver.objective_value == minimum
                and solver.best_objective_bound == minimum):
            # Both API doubles equal this small exact integer, with no rounding.
            result.update(status="exact", g=len(weights)-minimum,
                          minimum_cover_lower=minimum, minimum_cover_upper=minimum,
                          cover=cover)
            return result
    result.update(status="not_exact", error="integer optimum not certified")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("t", type=int)
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--memory-mib", type=int, default=1024)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    if args.memory_mib:
        cap = args.memory_mib * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    started = time.perf_counter()
    result = {"t": args.t, "engine": "cp_sat", "ortools_version": ortools.__version__,
              "workers": args.workers, "random_seed": 168,
              "timeout_ms": args.timeout_ms, "address_space_limit_mib": args.memory_mib}
    try:
        result.update(solve(args.t, args.timeout_ms, args.workers))
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
