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

## Points in every or no maximum set

`forced_points.py` uses the same exact hitting-set solver. For each prefix
it first computes g, then solves **twice for every point**: once with the
omission variable true (point excluded), and once with it false (point
required). A point is `forced` when exclusion reduces the optimum, `none`
when requirement reduces it, and `flexible` when both constrained maxima
equal g. Each query must close its integer objective bounds and return a
witness satisfying the corners, cardinality, and point constraint.
UNKNOWN or a timeout aborts without classifying that query.

The solver and context are fresh at every prefix. Queries within that
fixed prefix use temporary assumptions; no hard constraints or objectives
are accumulated between them. The first 16 prefixes are also checked by
enumerating every subset, intersecting and taking the union of **all**
maximum sets. Optional `--compare` checks already saved optima only after
the independent computation; they are never solver input.

```bash
experiments/.venv/bin/python experiments/forced_points.py --prefixes 40 --compare experiments/results.json --output experiments/forced-small.json
experiments/.venv/bin/python experiments/forced_points.py --prefixes 200 --timeout-ms 30000 --compare experiments/results.json --output experiments/forced-results.json
```

The CSV table has one row for every point of every prefix, with coordinates,
status, both constrained optima, and their losses relative to g. JSON adds
the unrestricted cover, timings, and tests of the jump criterion using
statuses from the **previous** prefix. Complete prefixes are flushed to an
ignored `.partial.jsonl` checkpoint. These are exact computational results
relying on Z3, not Lean proofs.

`analyze_forced.py` checks geometric and membership rules against every
table row, records counterexamples to a simple residue-class cover, and
generates a standalone HTML/SVG viewer with a prefix slider. It can also
show the preceding prefix and highlight the lower neighbors relevant to
the jump test. All plotting data is embedded; it needs no server or network.

```bash
python3 experiments/analyze_forced.py experiments/forced-results.json
```

Open `experiments/forced-viewer.html` in a browser. The analysis JSON
explicitly labels finite fitted rules as computations, rather than proved
general formulae. The small report can be analyzed with the same command
using `--output` and `--viewer` to choose separate output paths.

The saved full membership report covers all 200 prefixes through
`15116544`, with g = 134, 20,100 classifications and 40,200 constrained
queries. The requested previous-prefix jump test agrees in all 176 cases
with b > 0. Empirical diagonal-band and forced-corner rules fit this domain;
their general converses are unproved. The simple active-residue cover
already fails at 1536. Requiring a point can lose two: the first example
is 24 at t = 1417176, where the maximum drops from 101 to 99. See
`forced-analysis.json` for complete rule checks and counterexamples, and
`../NOTES.md` for interpretation and validation.

## Participating-colour candidate comparison

`candidate_formula.py` tests
`g_cand = |Σ(t)| - min(c_0(t), c_1(t), c_2(t))`, where c_j counts only
points of colour `(a-b) mod 3` that belong to a complete corner. It uses
the saved exact optima and needs only the Python standard library:

```bash
python3 experiments/candidate_formula.py
```

For every prefix, the program checks the candidate covers are feasible,
reconstructs coordinate and numerical corners independently, and validates
the saved exact objective bounds and omission witnesses. It also checks
the overlapping exact reports and compares the discrepancies with the
200-prefix extra-pair classifications. This computation does not rerun
MaxSAT or certify optimality independently of the original solver.

`candidate-results-through-100000000000.csv` gives all 452 requested
smooth cutoffs through 10^11, including t, exact g, g_cand, their difference
(`exact_g - g_cand`), lattice size, and colour counts. The candidate agrees
in 424 cases and is one too small in 28. `candidate-results.csv` includes
all 507 saved cutoffs, with 32 failures, also all of size one.
`candidate-results.json` records all rows and discrepancies, provenance,
and the membership comparison. Exact g is never below this achievable
candidate. In the first 200 prefixes the failures coincide exactly with
the ten recorded extra-pair prefixes, starting at 1536; forcing data is
not available at the later failures. All discrepancy rows are listed in
`../NOTES.md`. None of these computations is a Lean proof.

## Interval rule for the excess

```bash
python3 experiments/excess_rule.py
experiments/.venv/bin/python experiments/verify_excess_pairs.py
```

`excess_rule.py` reconstructs all 507 exact comparisons and tests five
interval/tie rules. The following rule fits all 507 cutoffs, with 32
positive cases and no mismatches:

```text
E(t)=1 iff there exists m >= 0 such that
  24*2^m <= t < 27*2^m
  and c_((m+2) mod 3)(t) = min(c_0(t), c_1(t), c_2(t)).
```

The specified colour must minimize the counts; a tie by itself is
insufficient. This is a finite fitted equivalence, not a proved general
formula. The interval has a direct geometric motivation: start from
that participating colour cover, remove omissions `(m+2,0)`, `(m+1,2)`,
`(m+3,1)`, and add `(m+1,1)`, `(m+3,0)`. The resulting cover is one
point smaller. Its feasibility was checked at all 89 cutoffs in these
intervals, and it achieves exact g at every excess cutoff.

`excess-results.csv` and `excess-results.md` list all 32 discrepancies with
factorizations, extra omitted pairs, colour counts, minimizing colours,
and normalized ratios to the largest powers of two and three. The CSV
retains exact fractions and long decimal values. `excess-results.json`
also records corrected optimal cover witnesses, predictions on all 507
cutoffs, and every mismatch of every tested rule. Neither logarithms nor
interval comparisons use floating-point arithmetic.

`verify_excess_pairs.py` checks that both pair points belong to no optimum.
It reuses 20 earlier constrained classifications and makes 44 fresh exact
requirement queries for the 22 later discrepancy cutoffs. Requiring any
of the 64 pair points lowers g by one. Exclusion is witnessed by the
saved optimal covers, which already omit both points. `excess-pairs.json`
records the source of every result and new constrained optimum witnesses.
Full membership of all other points beyond prefix 200 was not recomputed.

## Frozen predictions and new holdouts

```bash
python3 experiments/holdout_predictions.py
experiments/.venv/bin/python experiments/holdout_verify.py --python experiments/.venv/bin/python
```

`holdout_predictions.py` freezes the interval rule from commit `6ca0694`
through 10^14: 720 smooth cutoffs, 481 predicted jumps, and 213 new
cutoffs above the original 507. `predicted-1e14.json` and `.csv` record
all predictions; `predicted-1e14-jumps.txt` is the complete jump list.
The saved plan prioritizes the 13 new excess cases, the 42 distinct edge
neighbors, and 25 other cutoffs sampled with seed `16820261004`, then
tests the rest. A feasible numerical-corner cover is checked for every
prediction, without claiming that it is optimal.

`holdout_verify.py` launches `holdout_worker.py` in a fresh process for
each selected cutoff. The worker receives no formula, prediction or
proposed bound and solves the unrestricted hitting-set problem. Only
closed exact integer bounds and checked covers count as exact results.
Timeouts are retained and the run continues, so it can report verified
and unverified cutoffs separately. Worker peak resident memory uses
Linux `/proc/self/status` `VmHWM`; raw `getrusage` is recorded separately
because it can retain a high-water mark from previous process history.
The memory limit is virtual address space, rather than a resident-memory
cap. These computations are not Lean proofs.

The optional second backend is [Google OR-Tools CP-SAT](https://developers.google.com/optimization/cp/cp_solver),
distributed under [Apache 2.0](https://github.com/google/or-tools/blob/stable/LICENSE).
`holdout_cpsat_worker.py` independently generates the unrestricted Boolean
corner-cover model. It accepts only `OPTIMAL` with equal integer objective
bounds and a checked cover; feasible incumbents alone are recorded as
unverified. No formula, colour restriction, initial optimum or supplied
bound enters the optimization. Four workers and seed 168 are used by
default. Its original problem-specific code uses the documented API;
no published problem solver or DP code was copied.

```bash
experiments/.venv/bin/python -m pip install -r experiments/requirements-holdout.txt
experiments/.venv/bin/python experiments/validate_cpsat.py
python3 experiments/holdout_verify.py --python experiments/.venv/bin/python --backend cp_sat --timeout-ms 30000 --output experiments/holdout-cpsat.json
```

`validate_cpsat.py` checks all integer cutoffs 1..64 against exhaustive
subset enumeration, and six saved MaxSAT optima including positive
excess cases and window boundaries. `cpsat-validation.json` retains the
70 matching comparisons and the SHA-256 of the saved comparison file.

An individual unclosed query can be retried without changing the rule:

```bash
python3 experiments/holdout_verify.py --python experiments/.venv/bin/python --backend cp_sat --workers 8 --timeout-ms 120000 --only-t 11132555231232 --output experiments/holdout-cpsat-retry.json
python3 experiments/holdout_verify.py --python experiments/.venv/bin/python --backend cp_sat --workers 8 --timeout-ms 120000 --only-t 91507169819844 --output experiments/holdout-cpsat-retry-large.json
python3 experiments/holdout_results.py
```

`holdout_results.py` uses only the standard library. It checks the frozen
rule hash and original fitting-sample hash, rechecks every exact worker's
numerical cover and bounds, and rejects disagreements between exact
solvers. It then combines the old 507 prefixes with the new answers and
independently reconstructs all coordinate corners and participating-colour
counts using `candidate_formula.compare`. It refuses to emit a complete
report while any planned cutoff lacks an exact answer.

`holdout-results.json` and `.csv` are the new-prefix comparison and
cohort summary; raw solver reports retain bounds, witnesses, timeouts,
timings and memory. `results-1e14.json` and `.csv` contain the complete
combined exact table, keeping `results.json` as the original fitting
sample. `verified-1e14-jumps.txt` lists the independently computed jumps
for comparison with the frozen predicted list. These are finite exact
computations relying on solver answers; matching holdouts do not prove
the rule for every t or prove irrationality.

The saved completed run verifies **all 213 new cutoffs**, so the combined
domain has 720 exact prefixes through 10^14. There are **zero mismatches**
and 481 exact jumps, identical to the frozen predicted jump list. This
includes all 13 new excess cases, all 42 edge neighbors, and all 25 random
samples. The largest solved cutoff is `96402615118848`, with g=481.
The main CP-SAT run closed 211 queries; two eight-worker retries closed
the others. All 56 queries also closed by Z3 agree. Peak worker resident
memory over all runs was 209.69 MiB; no address-space cap was hit.

In `holdout-results.csv`, `difference` means exact g minus g_pred.
In `results-1e14.csv`, `difference` means exact g minus g_cand and
`prediction_difference` means exact g minus g_pred. The prediction
differences are all zero; the base colour candidate is one smaller
at 45 of the 720 cutoffs.
