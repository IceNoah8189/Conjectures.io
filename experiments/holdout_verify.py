#!/usr/bin/env python3
"""Run isolated exact-solver workers on the frozen holdout plan."""

import argparse
import csv
import json
from pathlib import Path
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, default=Path("experiments/predicted-1e14.json"))
    parser.add_argument("--python", default="/tmp/erdos168-venv/bin/python")
    parser.add_argument("--timeout-ms", type=int, default=10000)
    parser.add_argument("--memory-mib", type=int, default=1024)
    parser.add_argument("--engine", choices=("rc2", "maxres"), default="rc2")
    parser.add_argument("--backend", choices=("z3", "cp_sat"), default="z3")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--wall-budget-seconds", type=int, default=1800)
    parser.add_argument("--maximum-queries", type=int, default=0)
    parser.add_argument("--only-t", type=int, action="append", help="query only these planned cutoffs")
    parser.add_argument("--output", type=Path, default=Path("experiments/holdout-z3.json"))
    args = parser.parse_args()
    predictions = json.loads(args.predictions.read_text())
    by_t = {row["t"]: row for row in predictions["rows"]}
    started, rows = time.perf_counter(), []
    plan = predictions["selection_plan"]
    if args.only_t:
        requested = set(args.only_t)
        if not requested <= {item["t"] for item in plan}:
            raise ValueError("requested cutoff outside frozen holdout plan")
        plan = [item for item in plan if item["t"] in requested]
    with args.output.with_suffix(".partial.jsonl").open("w") as checkpoint:
        for selection in plan:
            if (time.perf_counter() - started >= args.wall_budget_seconds
                    or args.maximum_queries and len(rows) >= args.maximum_queries):
                break
            t = selection["t"]
            worker = ("experiments/holdout_worker.py" if args.backend == "z3"
                      else "experiments/holdout_cpsat_worker.py")
            command = [args.python, worker, str(t),
                       "--timeout-ms", str(args.timeout_ms),
                       "--memory-mib", str(args.memory_mib)]
            command += (["--engine", args.engine] if args.backend == "z3"
                        else ["--workers", str(args.workers)])
            query_started = time.perf_counter()
            try:
                completed = subprocess.run(command, capture_output=True, text=True,
                                           timeout=args.timeout_ms / 1000 + 10)
                if completed.returncode:
                    result = {"t": t, "status": "worker_failed", "returncode": completed.returncode,
                              "error": completed.stderr[-2000:]}
                else:
                    result = json.loads(completed.stdout)
            except subprocess.TimeoutExpired:
                result = {"t": t, "status": "hard_timeout", "error": "outer worker deadline exceeded"}
            result.update(tags=selection["tags"], g_pred=by_t[t]["g_pred"],
                          predicted_E=by_t[t]["predicted_E"],
                          wall_seconds=round(time.perf_counter() - query_started, 6))
            if result["status"] == "exact":
                result["difference"] = result["g"] - result["g_pred"]
                result["exact_E"] = result["g"] - by_t[t]["g_cand"]
            rows.append(result)
            checkpoint.write(json.dumps(result) + "\n")
            checkpoint.flush()
            print(f"query={len(rows)}/{len(plan)} t={t} status={result['status']} "
                  f"g={result.get('g')} predicted={result['g_pred']} "
                  f"seconds={result['wall_seconds']} "
                  f"peak_rss_kib={result.get('proc_peak_rss_kib')}", flush=True)
    exact = [row for row in rows if row["status"] == "exact"]
    failures = [row for row in rows if row["status"] != "exact"]
    mismatches = [row for row in exact if row["difference"]]
    report = {
        "predictions_source": str(args.predictions),
        "backend": args.backend,
        "engine": args.engine if args.backend == "z3" else "cp_sat",
        "workers": 1 if args.backend == "z3" else args.workers,
        "query_timeout_ms": args.timeout_ms,
        "address_space_limit_mib": args.memory_mib,
        "attempted_cutoffs": len(rows), "planned_cutoffs": len(plan),
        "exact_cutoffs": len(exact), "not_exact_cutoffs": len(failures),
        "largest_exact_cutoff": max((row["t"] for row in exact), default=None),
        "peak_worker_rss_kib": max((row.get("proc_peak_rss_kib", 0) for row in rows), default=0),
        "mismatches": mismatches, "failed_cutoffs": [row["t"] for row in failures],
        "unattempted_cutoffs": [row["t"] for row in plan[len(rows):]],
        "wall_seconds": round(time.perf_counter() - started, 6), "rows": rows,
        "memory_measure": "Linux /proc/self/status VmHWM for each isolated worker memory image; rusage is also recorded but can retain prior process history",
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    with args.output.with_suffix(".csv").open("w", newline="") as stream:
        fields = ["t", "status", "g_pred", "g", "difference", "predicted_E", "exact_E",
                  "wall_seconds", "proc_peak_rss_kib", "tags"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "|".join(row["tags"]) if key == "tags" else row.get(key)
                             for key in fields})
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=2))


if __name__ == "__main__":
    main()
