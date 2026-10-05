# Independent exact computation of g(t)

`exact_g.py` builds the lattice directly using integer products. Each point
has a Boolean omission variable; each forbidden corner requires at least
one of its three variables to be true. Z3 solves the resulting Boolean
hitting-set problem as MaxSAT: each retained point is a unit-weight soft
constraint, while every corner constraint is mandatory. This program
was written independently for this task. It uses no column-by-column
bitmask DP, copied problem-specific solver code, published value table, or assumed
formula for the jump set. The expected prefix is used only for comparison
after the optima have been computed.

The minimum soft cost h is the minimum number of omissions; g = k-h
for a prefix of k points. The program accepts an optimum only when the
solver returns SAT and its exact integer objective lower and upper bounds
coincide. The corresponding cover is checked directly against every
generated corner, and its size must equal the objective. UNKNOWN, a
timeout, or unequal bounds aborts; none is interpreted as an optimum.
It also checks that the minimum cover changes by zero or one as each
point is added. Z3's `rc2` engine uses unsatisfiable cores to solve MaxSAT;
the earlier `maxres` engine remains available through `--engine maxres`.
The initial version used slower standalone cardinality queries
(commit `a11f93f`).
Each prefix uses a fresh optimization object and a fresh Z3 context, with all hard clauses added
before the soft objective. An initial incremental-object run timed out
at t = 2448880128; rebuilding the same problem closed both bounds in
under a second in a separate trial. A timeout is a performance failure,
not a disagreement in g or in the jump list.
Reusing the global context also led to a timeout at t = 241864704,
although a standalone model closed this optimum in 0.14 seconds. Isolating
each query's context makes its Boolean expression construction independent
of prior queries. All result checks remain in place.
The isolated `maxres` extension timed out at t = 587068342272. A separate
`rc2` query closed that same optimum in about two seconds, motivating the
default-engine change. A query timeout still aborts the run.

This is an exact integer/Boolean computation relying on Z3's SAT/UNSAT
optimization answers, not a Lean proof or an independently checked proof certificate.
The program also compares all integer cutoffs through 64 with a separate
exhaustive subset enumeration using the numerical triples n, 2n, 3n.

For reproducible runs with Python 3.10 or later:

```bash
python3 -m venv experiments/.venv
experiments/.venv/bin/python -m pip install -r experiments/requirements.txt
experiments/.venv/bin/python experiments/exact_g.py --limit 288 --output experiments/small-results.json
experiments/.venv/bin/python experiments/exact_g.py --limit 100000000000 --timeout-ms 120000 --output experiments/results-1e11.json
experiments/.venv/bin/python experiments/exact_g.py --limit 470184984576 --timeout-ms 120000 --progress --output experiments/results.json
```

The JSON records g at every smooth number, all jumps, minimum-cover
witnesses, and exact rational density bounds. For arbitrary integer t,
g(t) equals the value at the last smooth number at most t, with g(0)=0.
The upper density bound adds all remaining smooth reciprocal terms,
computed exactly as 1 minus one third of the prefix's reciprocal sum.
No floating-point arithmetic is used in optimization or these bounds.
If the entire exact interval is strictly inside a single rounding cell,
the report certifies the density's rounding to ten decimal places.
When `--output` is supplied, completed rows are also flushed to an ignored
`.partial.jsonl` file. This diagnostic checkpoint survives an error and
is never read as input to the solver. The full `.json` report is written
only when every query and the brute-force checks succeed.

In this environment pip was unavailable. The pinned public PyPI wheel
was downloaded into `/tmp`, its SHA-256 checked, and extracted into a
temporary virtual environment. The wheel digest was
`dfad9e309d7010b1ff6bdb33f21570a1603ef4727373221c7117a74448f0cfef`.
The standard pip instructions above avoid that environment-specific step.

The experiment uses the [Z3 project](https://github.com/Z3Prover/z3),
distributed under the MIT licence (as recorded in the installed wheel's
metadata). The lattice model, checks, and reporting code here were written
for this experiment; no code from the user's DP or the literature was copied.

The saved results contain all 507 completed prefixes through 470184984576,
including 339 jumps. The 452-point prefix through 10^11 has 302 jumps.
The exact density interval is contained in the outward-rounded enclosure
`[0.800965754989229, 0.800965755015529]`, which certifies ten-place
rounding to `0.8009657550`. The requested `0.8009657549` is the ten-place
rounding of the sum truncated at 10^11. No listed jump disagrees, but the
infinite sum has the small rounding correction just described.

The original optional cutoff was 10^12. That run was stopped once the
completed checkpoint rows certified all ten places; the saved report uses
its actual final completed threshold. The command above reproduces that
domain directly, rather than requiring an interrupted run.
