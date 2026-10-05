#!/usr/bin/env python3
"""Check the new backend against exhaustive enumeration and saved MaxSAT."""

import argparse
import hashlib
import json
from pathlib import Path

from exact_g import brute_g
from holdout_cpsat_worker import solve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("experiments/cpsat-validation.json"))
    args = parser.parse_args()
    rows = []
    for t in range(1, 65):
        expected = brute_g(t)
        result = solve(t, 30000, 1)
        if result["status"] != "exact" or result["g"] != expected:
            raise AssertionError(f"exhaustive check failed at {t}")
        rows.append({"t": t, "g": result["g"], "comparison_g": expected,
                     "source": "exhaustive subset enumeration"})
    source = Path("experiments/results.json")
    saved = json.loads(source.read_text())
    old = {row["t"]: row for row in saved["rows"]}
    for t in (768, 864, 1536, 26121388032, 208971104256, 470184984576):
        result = solve(t, 30000, 4)
        if result["status"] != "exact":
            raise RuntimeError(f"saved MaxSAT check did not close at {t}: {result['solver_status']}")
        if result["g"] != old[t]["g"]:
            raise AssertionError(f"saved MaxSAT check failed at {t}")
        rows.append({"t": t, "g": result["g"], "comparison_g": old[t]["g"],
                     "source": str(source)})
    report = {"exhaustive_integer_cutoffs": 64, "saved_maxsat_cutoffs": 6,
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "mismatches": [], "rows": rows}
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}))


if __name__ == "__main__":
    main()
