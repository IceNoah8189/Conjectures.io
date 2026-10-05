# Erdős 168 part ii notes

## Sources

- Challenge copied unchanged from `conjectures-io/conjectures-tasks` commit `7cc9b5235000a107743dcce8fcd5f6069c34c0b6`, path `pool/tier-1/erdos-168-parts-ii-formalized`.
- Lean configuration follows `conjectures-io/conjectures-validator` commit `d24e86cab809e69d388417b9114ce8d34a2256fc`.
- Lean is pinned to `leanprover/lean4:v4.33.1`; Mathlib is pinned to `0df444a360eaa60ab8c11dca51a86af692955474` (`v4.33.1`).
- Formal Conjectures is pinned to audited commit `6a786f997e18e8f095762a2830d191b7e25e505e`, reconstructed by `scripts/setup-deps.sh` from its base commit and the checked patch in this repo.

## Progress

- Copied and committed the seven task files without edits.
- Installed Lean v4.33.1 in this workspace.
- Reconstructed the audited Formal Conjectures commit and confirmed the Lake project resolves Lean v4.33.1 and the validator's pinned Mathlib commit.
- `lake exe cache get` was attempted with `XDG_CACHE_HOME=/workspace/.cache`. The cache's `lakecache.blob.core.windows.net` endpoint was rejected by this environment's proxy (`CONNECT tunnel failed, response 403`, followed by rate limiting). No Mathlib library was built from source.
- The initial cloud compilation check stopped at the first import because the blocked cache prevented building its dependencies; its 0.717-second failed run was **not** a successful compilation time. The later successful check is recorded below.
- Local WSL build works: first compile of Challenge.lean took about 7 minutes; it reports the expected sorry warning.

## Definition of F (2026-10-04)

Read `AGENTS.md`, this file, `tasks/erdos-168-ii/Challenge.lean`, and
`vendor/formal-conjectures/FormalConjectures/ErdosProblems/168.lean`.
Also read the vendor's instructions and `lean/TaskSupport.lean` to check
how the challenge obtains its target type.

- `NonTernary S` means that for every natural number n, at least one of
  n, 2*n, and 3*n is absent from S. This forbids these particular triples,
  rather than all three-term arithmetic progressions.
- `IntervalNonTernarySets N` takes the powerset of `Finset.Icc 1 N` and
  filters it by this condition for n in `Finset.Icc 1 (N / 3)`.
  Division here is natural-number division, so N / 3 is rounded down.
  Only these n need checking: for positive n larger than N / 3, 3*n
  exceeds N. The n = 0 case is automatic because 0 is outside {1,...,N}.
- `F N` abbreviates `(IntervalNonTernarySets N).sup Finset.card`.
  It is a natural number: the largest cardinality of any admissible subset,
  not the number of admissible subsets. The empty set is always admissible.
  The supplied small cases are F(0)=0, F(1)=1, F(2)=2, and F(3)=2.
- `mem_IntervalNonTernarySets_iff` proves that this finite filter is
  equivalent to `NonTernary S` together with S being a subset of {1,...,N}.
  `F_eq_card` identifies F with the size of any cardinality optimizer.
- The ratio in the target is real division after coercing F(N) and N
  to real numbers. Its value at N = 0 is 0 in Lean; this single value
  does not affect the behavior at infinity.
- Part ii asks about irrationality of the `atTop` limsup. The vendor labels
  it `research open`. Its separate limit-existence theorem is labelled
  solved but still has an unfinished Lean proof. Neither unfinished
  declaration is a completed proof of the requested result.

## Planning step (2026-10-04)

- Added `PLAN.md` with small proposed lemmas for finite maximization,
  decomposition by the factor coprime to 6, a convergent series formula,
  identification of the limsup, and a conditional irrationality argument.
- The central remaining issue is a structural theorem about the actual
  component optima strong enough to prove arithmetic separation. The plan
  explicitly identifies this as unresolved, rather than claiming a proof
  of the open question.
- No proof was written and no task or vendor Lean file was changed.
- Wallets, keys, and secret files were not accessed.

## Challenge compilation check (2026-10-04)

- Ran exactly `lake env lean tasks/erdos-168-ii/Challenge.lean` in the
  repository root. It completed successfully with exit code 0.
- Output contained the existing `declaration uses sorry` warning at line 6
  and module-docstring linter warnings at lines 4, 9, and 10. There were no
  errors. This confirms compilation of the unchanged challenge scaffold;
  it does not validate a completed proof.
- `git diff --check` passed. Checked that neither the challenge nor the
  vendored problem file had any changes.
- Committed the plan and definition notes as `74ea6a0` before recording
  this compilation result. Git needed an approved escalation because the
  sandbox exposes `.git` as read-only.
- Remaining work is mathematical research on the irrationality stage in
  PLAN.md, followed by proof development and submission validation.

## Verified mathematical facts and computations supplied by the user (2026-10-04)

The following facts and numerical checks were supplied by the user as
verified. They are not proved in Lean in this repository. The reported
brute-force checks and exact DP computation have not been rerun here;
no DP source or computational certificate was supplied with these notes.

- Write every positive integer uniquely as n = q * 2^a * 3^b with
  gcd(q,6) = 1. A forbidden triple n, 2n, 3n stays in the same q-class,
  so these classes are independent for this problem.
- Let g(t) be the largest cardinality of a set of lattice points (a,b)
  with a,b ≥ 0 and 2^a * 3^b ≤ t that contains no whole triple
  (a,b), (a+1,b), (a,b+1). Set g(0) = 0. Then
  F(N) = Σ over 1 ≤ q ≤ N with gcd(q,6) = 1 of g(floor(N/q)).
  The user checked this identity against brute force for
  N = 3, 10, 30, 60, and 100.
- g can increase only at 3-smooth numbers, meaning numbers 2^a * 3^b.
  Every increase has size exactly one. Define the jump set
  J = {s ≥ 1 : g(s) - g(s-1) = 1}. A smooth number can have increment
  zero; the claim is not that every smooth number is a jump.
- The reported first jump points are:
  1, 2, 4, 6, 8, 12, 16, 24, 32, 36, 48, 64, 72, 96, 128, 144,
  162, 216, 256, 288, 324, 432, 512, 576, 648, 768, 972, 1024, …
- An exact column-by-column bitmask DP found 302 jumps among the 452
  smooth numbers at most 10^11. This is finite computational evidence,
  not an exact rule for all future jump points or a Lean certificate.
- Consequently the limit has the series expression
  L = (1/3) * Σ over s in J of 1/s. Its reported numerical value is
  approximately 0.80096575. No certified error interval was supplied for
  this decimal, so it should not be used as a proved precision bound.
- The hard part remains an exact rule for which smooth numbers are jumps
  and an irrationality proof for that particular series. PLAN.md now uses
  g and J consistently and treats these facts as inputs for future
  formalization, not as already available Lean theorems.

## Related work and reuse checks (2026-10-04)

- The accepted Erdős 1062(ii) result is a related example of a density
  problem handled by a coefficient expansion and a Diophantine argument.
  The [acceptance record](https://conjectures.io/results/8d59a0af-6762-4606-93c9-72dd356a57bc)
  credits submitter JenW1N. The linked
  [exposition by Liam Kruer and Jensen Kohlmeyer](https://conjectures.io/papers/erdos1062ii.pdf?v=20260922-authors),
  dated 22 September 2026, describes a series of rank increments,
  a coefficient expansion, and a contradiction using small nonzero
  linear forms in rational powers of two and three. It is an exposition
  of the accepted formal artifact; its prose is not itself kernel-verified.
- The 1062 condition forbids any element dividing two distinct others,
  whereas 168 forbids only n, 2n, 3n. In 1062, divisibility can connect
  distinct q-classes. Its formulas and arithmetic hypotheses therefore
  require a fresh applicability check before use for 168.
- User-supplied lead: a public Lean proof of limit existence may be in
  [baobingzhang/jsp-000165-erdos168-lean](https://github.com/baobingzhang/jsp-000165-erdos168-lean).
  Web attempts to read the repository, API metadata, README, and LICENSE
  failed; no licence, theorem statement, or proof status was verified.
  No code was copied. Before any reuse, inspect the actual licence and
  relevant file headers, record the revision and author credit, and check
  the target definition, dependencies, and unfinished proof assumptions.

## Documentation revision checks (2026-10-04)

- Read the current AGENTS.md, NOTES.md, and PLAN.md, then added the user's
  verified facts with their computational scope and updated the stages.
- Checked the 1062 acceptance record and its linked PDF using web access;
  the 168 repository remains a lead requiring inspection.
- `git diff --check` passed; the revision changes only NOTES.md and PLAN.md.
  No proof was written or Lean file changed, so the previous challenge
  compilation check remains the relevant check; it was not rerun.
- No wallet, key, or secret file was accessed.

## Independent solver: first successful check (2026-10-04)

- Wrote `experiments/exact_g.py` independently as an exact Boolean
  hitting-set model. It does not use the user's column-by-column bitmask
  DP, external experiment code, an assumed jump rule, or published optima.
  The comparison prefix is inspected only after solving.
- Z3 5.1.0 checks cardinality-bounded SAT/UNSAT queries. The minimum
  cover size can stay constant or increase by one on adding a point;
  each query distinguishes these cases. Every returned cover is checked
  directly against every forbidden corner. UNKNOWN aborts the run.
- This is an exact Boolean computation relying on Z3, not a Lean theorem
  or an independently checked proof certificate. JSON stores witnesses
  and the SAT/UNSAT outcomes for later replay.
- Python had no pip. Created `/tmp/erdos168-venv` without pip, downloaded
  the pinned PyPI wheel with approved network access, checked its SHA-256,
  and extracted it into that temporary environment. The dependency and
  normal installation commands are recorded in `experiments/README.md`.
- Command: `/tmp/erdos168-venv/bin/python experiments/exact_g.py --limit 288 --output experiments/small-results.json`.
  Exit code 0: 29 smooth points, g(288)=20, and all 20 requested jumps
  agree exactly, including the absence of extra jumps through 288.
- A separate exhaustive numerical subset enumeration agrees with the
  Boolean solver at every integer cutoff from 0 through 64.
- The larger density computation and literature review are in progress.
  No Lean file, wallet, key, or secret file has been touched.

## Literature search and solver performance update (2026-10-04)

- Primary historical source: R. L. Graham, H. S. Witsenhausen, and
  J. H. Spencer, [On extremal density theorems for linear forms](https://mathweb.ucsd.edu/~ronspubs/77_05_extremal_density.pdf),
  in Number Theory and Algebra (H. Zassenhaus, editor), Academic Press,
  1977, pp. 103–109. Its general density theorem gives the increment
  series for this problem; see also Theorem 2 as cited in the recent
  preprint below. This is a density representation through finite optima,
  not a closed formula for those optima.
- Fan Chung, Paul Erdős, and Ronald Graham,
  [On sparse sets hitting linear forms](https://math.ucsd.edu/~fan/wp/linear.pdf),
  Number Theory for the Millennium I, 2002, pp. 257–272, studies the
  equivalent problem of hitting all lattice corners. In Section 4 it
  compares the minimum hitting number with a boundary-corrected choice
  among three residue classes and leaves equality conjectural. Its f(k)
  counts omissions, so our g(d_k) = k - f(k). Section 5 also asks whether
  the candidate formula always holds and how to compute large prefixes.
- Nikola Veselinov,
  [Extremal densities for forbidden configurations in S-smooth numbers](https://arxiv.org/html/2604.15515v1),
  arXiv:2604.15515v1, submitted 16 April 2026, gives an asymptotic
  estimate g(t) = (2/3)*Psi_{2,3}(t) + O(log t), the density series,
  and computable reciprocal-tail bounds. Propositions 6.2–6.3 show that
  globally nested optimizers are impossible and characterize a jump
  by the existence of a suitable optimizer of the previous prefix.
  Powers of two always jump. This criterion still requires solving an
  optimization problem; it is not an explicit rule for all jumps.
- Conclusion of this search: no proved closed formula for the exact g(t),
  or explicit complete jump rule, was found in these sources. The known
  exact series and optimizer-based criterion must be distinguished from
  such a formula. This is a scoped literature finding, not proof that no
  formula exists anywhere. Searches included the three historical authors,
  the exact forbidden triple, recent work on problem 168, and S-smooth
  forbidden configurations; no later resolving paper was identified.
- [OEIS A386439](https://oeis.org/A386439), contributed by Sean Eberhard
  in September 2025, reports 0.80096575500655898909… and lists irrationality
  as open. This is an external numerical cross-check, not input to the
  independent solver. No linked SageMath script or external experiment
  source code was read or copied.
- The original cardinality-query implementation became slow above about
  150 points, so its large run was stopped. The program now uses Z3's
  exact `maxres` MaxSAT engine on the same independently generated hard
  corner clauses, with one unit soft clause per retained point. It accepts
  results only when the exact integer objective bounds coincide and the
  cover has the corresponding size. The small run through 288 was repeated
  successfully, including all brute-force checks through 64. The larger
  run with this formulation is in progress.

- Performance follow-up: the incremental optimization run returned
  UNKNOWN (`sat.canceled`) at t=2448880128 after its 120-second query
  limit. It produced no completed large-domain report. A fresh MaxSAT
  model for this same prefix closed both bounds in about 0.46 seconds.
  The final implementation rebuilds each prefix with hard clauses before
  soft clauses, and again passes the full small-domain check. It also
  independently reconstructs numerical triples to check completeness of
  the lattice clauses at every prefix. A run through 10^12 is in progress
  to obtain tighter density bounds and check the user's 10^11 count.

- The fresh-object run still reused the global Z3 context and timed out
  at t=241864704. A standalone query closed the same optimum in 0.14
  seconds. The implementation now isolates every prefix in a fresh Z3
  context as well as a fresh optimization object. The small-domain run
  passes again, and the ongoing large run has passed both earlier timeout
  points. No UNKNOWN answer has been used as an optimum.

- The isolated `maxres` run completed every prefix through 10^11,
  confirming 302 jumps among 452 smooth numbers, but its optional 10^12
  extension timed out at t=587068342272. A separate exact `rc2` query
  solved that prefix with cover size 171 in about two seconds. The
  program now defaults to `rc2`, with the same exact objective-bound and
  witness checks, and records the engine in its report. The small-domain
  checks pass with this engine as well. Every completed row is flushed
  to a diagnostic checkpoint, preventing loss of progress on a later
  error; checkpoint data is never an optimization input. A final run is
  in progress to retain the full density calculation.

## Completed independent comparison through 10^11 (2026-10-04)

- Saved `experiments/results-1e11.json` from the final run's completed
  checkpoint rows, after checking that their thresholds equal every
  smooth number at most 10^11 and rerunning the exhaustive checks through
  64. It can be reproduced directly with:
  `/tmp/erdos168-venv/bin/python experiments/exact_g.py --limit 100000000000 --timeout-ms 120000 --output experiments/results-1e11.json`.
- The exact solver independently confirms g(10^11)=302 on 452 points,
  hence 302 jumps. All 20 requested jump points through 288 agree, with
  no additional jump in that range. All integer cutoffs 0 through 64 agree
  with exhaustive enumeration. Every prefix has matching integer objective
  bounds and a cover checked against independently reconstructed triples.
- The computed truncated density sum is exactly
  15545471736978701297281 / 19408409961765342806016,
  approximately 0.80096575492806223493. It rounds to the user's
  0.8009657549 at ten decimal places.
- By the classical jump-series identity, the complete infinite sum lies
  between this lower bound and approximately 0.80096575504550563262.
  The exact upper bound is 215909329711917929261 / 269561249468963094528;
  the interval width is less than 1.175e-10. The exact fractions are in
  the report. Thus the requested decimal is an accurate approximation;
  it is below even the truncated sum by about 2.81e-11, so it should not
  be read as an exact value or a certified full-series rounding.
- No disagreement was found with the requested jump list or the reported
  302/452 count. The optional extension beyond 10^11 is still running
  solely to narrow the interval and resolve ten-place rounding of the
  infinite sum. These are computational results, not Lean proofs.

## Final density result and verification (2026-10-04)

- The final exact run retained all 507 completed smooth prefixes through
  t=470184984576, with g(t)=339. Saved them in `experiments/results.json`.
  The optional run toward 10^12 was deliberately stopped after the
  completed results certified ten-place rounding; it did not compute all
  534 prefixes through 10^12. No interrupted or UNKNOWN query contributes
  to either saved result file.
- Using the classical series identity and the exact remaining smooth
  reciprocal tail, the infinite density lies in the outward-rounded
  decimal enclosure [0.800965754989229, 0.800965755015529]. Its exact
  rational interval has width approximately 2.62987e-11. Both endpoints
  lie strictly between the rounding boundaries 0.80096575495 and
  0.80096575505, so the density rounds to **0.8009657550** at ten places.
- Precision difference: 0.8009657549 is a good approximation and is the
  ten-place rounding of the 10^11 truncated sum, but the infinite sum is
  between about 8.923e-11 and 1.156e-10 larger. This is the only numerical
  correction found. All 20 requested jumps agree; the additional eight
  listed jumps through 1024 also agree, as does the 302/452 count.
- `experiments/exact_g.py` now certifies ten-place rounding automatically
  when its exact interval fits strictly within one rounding cell. Both
  saved large reports were regenerated from completed checkpoint rows,
  checking their full smooth-number domains and the exhaustive oracle
  through 64. The smaller cutoff does not resolve ten-place rounding;
  the final cutoff does. JSON retains exact fractions, objective bounds,
  and a minimum-cover witness at each threshold.
- Direct reproduction commands (normal virtual-environment installation
  is documented in `experiments/README.md`):
  `/tmp/erdos168-venv/bin/python experiments/exact_g.py --limit 100000000000 --timeout-ms 120000 --output experiments/results-1e11.json`;
  `/tmp/erdos168-venv/bin/python experiments/exact_g.py --limit 470184984576 --timeout-ms 120000 --progress --output experiments/results.json`.
  The saved reports were assembled from the already completed final-run
  checkpoint rather than rerunning these expensive optimizations.
- `git diff --check` passed. Only experiments and documentation changed;
  the challenge and all task statements remain unchanged. No Lean proof
  was written, and no wallet, key, or secret file was accessed. The
  remaining mathematical issue is the exact jump rule and irrationality
  argument described in PLAN.md; the literature search found no proved
  closed formula for g in the sources reviewed.

## Forced-point experiment: solver and small verification (2026-10-04)

- Added `experiments/forced_points.py`, reusing the independent Boolean
  hitting-set MaxSAT model through a new `CoverSolver` helper. At every
  prefix it computes the unrestricted maximum and then solves once with
  each point excluded and once with that point required. Both constrained
  maxima are saved; `forced` means exclusion lowers g, `none` means
  requirement lowers g, and `flexible` means both preserve g. Every query
  requires matching integer lower/upper objective bounds and a checked
  witness. Assumptions apply only to that query. A fresh model and Z3
  context are used at each prefix, without accumulating prefix vertices.
- Performance trials of fixed-cardinality SAT timed out at 150 points.
  Reusing the MaxSAT model with temporary point assumptions was much
  faster, so the actual experiment computes constrained optima directly.
  No timed-out query is treated as a membership result.
- Command:
  `/tmp/erdos168-venv/bin/python experiments/forced_points.py --prefixes 40 --compare experiments/results.json --output experiments/forced-small.json`.
  All 40 prefixes through 972 completed: 820 point classifications,
  1,640 constrained queries, and 40 unrestricted queries. All computed g
  values agree with the previously saved independent results. A separate
  exhaustive oracle enumerated every maximum set at each of the first 16
  prefixes, confirming g and the intersection/union classifications.
- The requested criterion was checked against the previous prefix, not
  the prefix including the new point. All 30 cases with b>0 agree:
  a jump occurs exactly when at least one of the two lower neighbors is
  not forced previously. Powers of two always jump. Also, the new point
  is forced in the new prefix exactly when it is a jump, in all 40 cases.
- Points belonging to no optimum do occur. At t=6 the unique optimum is
  {1,3,4,6}, so 2 belongs to none; at t=18 only 16 is forced and no point
  belongs to none. This shows that membership need not persist as the
  threshold grows. The saved CSV/JSON tables contain all small results;
  a larger run is now computing 200 prefixes before drawing geometric
  conclusions. These results are computational, not Lean proofs.
- Regression command:
  `/tmp/erdos168-venv/bin/python experiments/exact_g.py --limit 64 --output /tmp/erdos168-refactor-check.json`.
  It passed all integer-cutoff exhaustive checks through 64 and the
  expected jump comparison. No Lean file or task statement was changed.

## Forced-point experiment: analysis tools verified (2026-10-04)

- Added `experiments/analyze_forced.py`. It tests local corner rules,
  incident-corner degrees, period-three residue classes (a-b modulo 3),
  and the losses under point constraints, saving all counterexamples.
  It also generates an offline HTML/SVG lattice viewer with a slider for
  prefixes and a view of the preceding prefix's lower neighbors. The
  viewer is a research artifact; all data is embedded locally.
- The analysis ran successfully on all 820 rows of the small report.
  The following empirical converses fit that report: every `none` point
  completes a corner whose other two points are forced, and requiring
  any point reduces the maximum by at most one. These are candidates to
  test on the larger report, not assumptions in the solver or Lean proofs.
  The easy direction of the first rule holds generally: a point cannot
  coexist with two forced points completing a corner.
- Additional validation rebuilt 42 selected constrained problems at
  prefixes 40, 45, 100, and 150, using a fresh solver/context **per query**
  and the alternative `maxres` engine. All constrained optima matched the
  main run's temporary-assumption `rc2` queries, including all three
  membership statuses where present.
- The viewer's JavaScript passed 80 rendering-logic checks (the current
  and previous views of all 40 small prefixes) in V8 with a minimal DOM.
  In particular, its t=6 view reports four forced points and one `none`
  point. No full browser is available here, so this check covers rendering
  logic and point counts, not browser layout. The 200-prefix run continues.

## Forced-point experiment: complete 200-prefix results (2026-10-04)

The run completed **every prefix from 1 through 200**, ending at
t=15116544 = 2^8*3^10, with g(t)=134. It independently recomputed 200
unrestricted optima and made exactly 40,200 constrained solves: one
exclusion and one requirement for each of 20,100 point/prefix pairs.
All integer objective bounds closed, all returned witnesses passed the
corner/cardinality/point checks, and all g values agree with the earlier
saved report. No conjectural membership or jump rule entered the solver.
The run took approximately 1,224 seconds. A separate 300-point performance
trial was stopped during its constrained queries; it contributes no rows
to this complete-prefix report.

Commands:

```bash
/tmp/erdos168-venv/bin/python experiments/forced_points.py --prefixes 200 --timeout-ms 30000 --compare experiments/results.json --output experiments/forced-results.json
python3 experiments/analyze_forced.py experiments/forced-results.json
```

Saved artifacts:

- `experiments/forced-results.csv`: the complete table, including (a,b),
  weight, status, both constrained maxima, and both losses.
- `experiments/forced-results.json`: optima, unrestricted cover witnesses,
  classifications, previous-prefix jump tests, and timings.
- `experiments/forced-analysis.json`: all tested rules, counts, and explicit
  counterexamples, including the unsuccessful candidate below.
- `experiments/forced-viewer.html`: offline lattice viewer; move the slider
  through all 200 prefixes or show the preceding prefix with the two lower
  neighbors highlighted. Hovering shows both constrained maxima.

Across point/prefix pairs there are 7,732 forced, 2,732 `none`, and 9,636
flexible classifications. These counts include the same lattice point at
different prefixes. There are 14 prefixes with a unique optimum and 17
prefixes where every point is flexible. Representative rows:

| Prefix | t | g | Forced | None | Flexible |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 6 | 4 | 4 | 1 | 0 |
| 10 | 18 | 7 | 1 | 0 | 9 |
| 24 | 162 | 17 | 17 | 7 | 0 |
| 40 | 972 | 27 | 10 | 0 | 30 |
| 45 | 1536 | 31 | 31 | 14 | 0 |
| 61 | 6144 | 42 | 42 | 19 | 0 |
| 100 | 93312 | 67 | 1 | 0 | 99 |
| 149 | 1417176 | 101 | 99 | 47 | 3 |
| 198 | 14155776 | 132 | 0 | 0 | 198 |
| 200 | 15116544 | 134 | 124 | 61 | 15 |

### Geometry and rules fitting all computed cases

The visible structure is period-three diagonal bands, indexed by
(a-b) modulo 3, with occasional changes near the boundary. Forcing is
also present deep inside the lattice: at t=1417176, (3,3), of weight 216,
is forced, while (5,3), of weight 864, belongs to no optimum. Both weights
are much smaller than t. At other prefixes nearly everything is flexible,
so one fixed band pattern cannot describe all thresholds.

The following statements fit **all 200 computed prefixes**, but the
geometric statements and the converse in the corner rule remain empirical:

1. If no point is `none`, all forced points that participate in at least
   one corner lie in a single residue class of (a-b) modulo 3. Isolated
   points are allowed outside that class.
2. If `none` points occur, they all lie in one residue class, except
   possibly two additional points of the form (a,1) and (a+2,0). There
   are 105 prefixes with no `none` points, 85 with just one residue class,
   and 10 with this extra pair. For example, at t=1536 the unique optimum
   omits 12 points of residue 2 and also (7,1), of weight 384, and (9,0),
   of weight 512, both of residue 0. The full table records all ten
   exceptions; a pair can persist into the next prefix.
3. A point is `none` **if and only if** some incident corner has its other
   two points forced. This fits all 20,100 classifications. The direction
   from a forced pair to `none` follows directly from corner avoidance;
   the reverse direction has only been checked computationally here. The
   corner can have any of its three positions occupied by the `none`
   point; checking only its two successors would fail, e.g. at t=72.
4. All isolated points are forced, and a point in only one corner is
   never `none`. These have short general arguments: an isolated point
   can always be added; for a point in a single corner, an optimum
   omitting it can include it after exchanging at most one other point.

These rules do not yet give a formula for the forced set or for g. In
particular, the corner rule uses the forced set as input, and does not
determine that set from the lattice alone. Establishing the fitted
converses or turning the bands and boundary corrections into an explicit
rule remains work for the proof plan. Nothing here is proved in Lean.

### Relation to jumps: requested criterion confirmed

All **176** additions with b>0 satisfy the requested equivalence, using
the optimum family of the **previous** prefix:

```text
2^a*3^b jumps
  iff (a,b-1) is not forced previously
       or (a+1,b-1) is not forced previously.
```

"Not forced" includes both flexible and `none` points: it means at least
one previous optimum omits that point. This is the same existential
condition as "some optimum omits one of the two lower neighbors."
For example, the addition of 6 is a jump: at t=4, 2 is flexible and 4 is
forced. The addition of 9 is flat: at t=8, both 3 and 6 are forced.
There are no disagreements. The 24 powers of two also all jump, giving
134 jumps and 66 flat additions in total.

There is also a short ordinary mathematical justification (not a Lean
proof). Adding a point with b>0 creates exactly one new corner, with those
two lower neighbors. An old optimum omitting one neighbor can be extended
by the new point. Conversely, a jump optimum must include the new point;
deleting it gives an old optimum omitting at least one lower neighbor.
The one-point bound makes these implications equivalent to a jump.

In every computed case the new point is forced exactly when it jumps,
and is flexible when it is flat; it is never `none`. This also follows
directly: a jump optimum must contain it, while a flat prefix has an old
optimum without it and an optimum obtained by exchanging one lower
neighbor for it. Powers of two are isolated on addition and are forced.
Thus a flat addition is precisely the case where both lower neighbors
were forced, even though adding that point can change earlier forcing.

### Counterexamples and verification limits

- The simple rule "omit the smallest active residue class" fails at
  ten computed thresholds. Here active means participating in a corner,
  so isolated points are retained. The first failure is t=1536: each
  active residue class has 15 points, but the exact minimum omissions
  is 14, so g=31 rather than the candidate's 30. At every recorded failure
  this candidate is worse by one. This tests only the simple uncorrected
  choice, not the boundary-corrected conjecture discussed in the earlier
  literature entry.
- The extra small-sample guess that requiring any point loses at most
  one is **false**. Its first counterexample is prefix 149, t=1417176:
  g=101 but requiring 24=(3,1) gives 99. There are 29 loss-two points at
  this prefix, all explicitly saved, and no further loss-two cases in
  the other 199 computed prefixes. Fresh `rc2` and `maxres` models both
  confirmed the first counterexample with omission bounds 50=50. This
  supersedes the preliminary small-sample observation above.
- The first 16 prefixes were independently verified by enumerating all
  subsets and intersecting/unioning every optimum. The 42 fresh-model
  cross-checks described above also passed. The final CSV and embedded
  viewer data were checked against every JSON point row. Solver answers
  are trusted computational evidence; no independently checked UNSAT
  certificates or Lean membership proofs were produced.
- `git diff --check` passed. The challenge and theorem statements are
  unchanged. No wallet, key, or secret file was accessed. The remaining
  mathematical task is still an exact general rule and the irrationality
  argument; finite patterns by themselves do not establish either.

## Participating-colour candidate: all saved exact cutoffs (2026-10-04)

Tested the candidate requested by the user:

```text
Σ(t) = {(a,b) : a,b >= 0 and 2^a*3^b <= t}
c_j(t) = number of points participating in a corner with (a-b) mod 3 = j
g_cand(t) = |Σ(t)| - min(c_0(t), c_1(t), c_2(t))
difference = exact g(t) - g_cand(t)
```

The comparison uses the already saved exact results. It covers all **452
smooth cutoffs at most 10^11**, ending at 99179645184. Since the exact
report also contains 55 further cutoffs, the full comparison additionally
covers all **507** saved cutoffs through 470184984576. No MaxSAT rerun was
needed, and no Lean was written.

Added `experiments/candidate_formula.py`, using only the Python standard
library. For each prefix it constructs lattice corners from coordinates,
takes their union to identify participating points, and counts the three
colours. It checks each colour-class omission set meets every corner in
exactly one point. It independently reconstructs the numerical triples
{n,2n,3n}, checks the corner/participation correspondence, and rechecks the
saved optimum's equal integer objective bounds and omission witness.
The complete domains and overlapping g values of both exact result files
also agree. These checks reuse the original exact solver answers; they
do not independently prove optimality or produce Lean certificates.

Reproduction command:

```bash
python3 experiments/candidate_formula.py
```

The full requested table of t, exact g, candidate g, and difference is in
`experiments/candidate-results-through-100000000000.csv` (452 rows).
`experiments/candidate-results.csv` contains all 507 rows. Both tables
also give |Σ(t)| and c_0, c_1, c_2. The JSON report
`experiments/candidate-results.json` saves the complete rows, all
discrepancies, source-file SHA-256 hashes, verification results, and the
comparison with the forcing data. Both CSV files were read back and
checked row-for-row against the JSON report.

### Achievability check and outcome

**Exact g was never below g_cand**, in either domain. There is also a
general elementary reason for this lower bound: the three points of a
corner have colours r, r+1, and r-1 modulo 3, so exactly one point of
each colour. All three participate in a corner by definition. Removing
every participating point of any chosen colour therefore destroys every
corner while retaining all isolated points. Choosing the smallest colour
class leaves a feasible set of cardinality g_cand. This is a plain-English
argument, not a Lean proof.

Among the 452 cutoffs through 10^11, the candidate equals exact g in
**424 cases** and is **one too small in 28 cases**. Among all 507 saved
cutoffs, it equals exact g in **475 cases** and is **one too small in 32
cases**. No larger gap was found. Thus the candidate is false as an exact
formula; the finite observation that the gap is always zero or one is
not a proved general upper bound.

Every discrepancy through 10^11 is listed here; all other requested
cutoffs have difference zero:

| t | Exact g | g_cand | Exact minus candidate |
| ---: | ---: | ---: | ---: |
| 1536 | 31 | 30 | +1 |
| 6144 | 42 | 41 | +1 |
| 12288 | 48 | 47 | +1 |
| 786432 | 93 | 92 | +1 |
| 3145728 | 111 | 110 | +1 |
| 3188646 | 112 | 111 | +1 |
| 6291456 | 121 | 120 | +1 |
| 6377292 | 122 | 121 | +1 |
| 12582912 | 131 | 130 | +1 |
| 12754584 | 132 | 131 | +1 |
| 25165824 | 142 | 141 | +1 |
| 25509168 | 143 | 142 | +1 |
| 50331648 | 153 | 152 | +1 |
| 51018336 | 154 | 153 | +1 |
| 402653184 | 189 | 188 | +1 |
| 408146688 | 190 | 189 | +1 |
| 1610612736 | 215 | 214 | +1 |
| 1632586752 | 216 | 215 | +1 |
| 3265173504 | 229 | 228 | +1 |
| 6530347008 | 243 | 242 | +1 |
| 12884901888 | 257 | 256 | +1 |
| 13060694016 | 258 | 257 | +1 |
| 25769803776 | 272 | 271 | +1 |
| 26121388032 | 273 | 272 | +1 |
| 27518828544 | 273 | 272 | +1 |
| 27894275208 | 274 | 273 | +1 |
| 51539607552 | 287 | 286 | +1 |
| 52242776064 | 288 | 287 | +1 |

The four additional discrepancies in the saved extension beyond 10^11
are:

| t | Exact g | g_cand | Exact minus candidate |
| ---: | ---: | ---: | ---: |
| 103079215104 | 303 | 302 | +1 |
| 104485552128 | 304 | 303 | +1 |
| 206158430208 | 319 | 318 | +1 |
| 208971104256 | 320 | 319 | +1 |

### Comparison with the extra-pair prefixes

Within the first 200 prefixes, the candidate fails **exactly** at the
ten extra-pair thresholds already recorded above:
1536, 6144, 12288, 786432, 3145728, 3188646, 6291456, 6377292,
12582912, and 12754584. The script reconstructed those extra pairs from
the saved `none` classifications and verified equality with both lists
in `experiments/forced-analysis.json`. There are no missing or additional
failures in that classified domain.

In particular, **t=1536 is the first discrepancy**: |Σ|=45 and
(c_0,c_1,c_2)=(15,15,15), so g_cand=30 while exact g=31. This agrees
with the unique optimum and its exceptional pair (7,1), (9,0) in the
previous notes.

The other 18 failures through 10^11, and the four extended failures, are
beyond the 200-prefix forcing dataset. Their g discrepancy is verified,
but membership in every/no optimum was not computed there, so they
cannot yet be identified as extra-pair prefixes from these results.
The observed extra-pair match is confined to the domain with membership
data; it is not an extrapolated general equivalence.

`git diff --check` passed. Only the comparison program, its tables/report,
and documentation changed. The challenge and all Lean statements remain
unchanged; no wallet, key, or secret file was accessed. Remaining issues
include a proved boundary correction or different exact formula for g,
and the irrationality argument.

## Excess E: factorization, boundary pairs, ratios and interval rules (2026-10-04)

Enriched all 32 cutoffs where exact g exceeds the participating-colour
candidate: the 28 through 10^11 and all four in the saved extension.
Each has E(t)=g(t)-g_cand(t)=1. The table below records its factorization,
extra omitted pair, all three participating-colour counts, every minimizing
colour (including whether the minimum is tied), and the requested ratios.
Ratios in the displayed table are rounded to nine decimal places; exact
fractions, long decimals, floor-logarithm exponents, pair weights, g and
candidate g are preserved in `experiments/excess-results.csv` and JSON.
All logarithms and interval decisions were computed by integer powers,
never floating-point logarithms.

The first 28 rows have t <= 10^11; the last four are the extension.

| t | Factorization | Extra omitted pair (a,b) | (c0,c1,c2) | Minimizers | t / 2^floor(log2 t) | t / 3^floor(log3 t) |
| ---: | --- | --- | --- | --- | ---: | ---: |
| 1536 | 2^9 * 3^1 | (7,1), (9,0) | (15,15,15) | 0,1,2 (tie) | 1.500000000 | 2.106995885 |
| 6144 | 2^11 * 3^1 | (9,1), (11,0) | (21,20,20) | 1,2 (tie) | 1.500000000 | 2.809327846 |
| 12288 | 2^12 * 3^1 | (10,1), (12,0) | (23,24,23) | 0,2 (tie) | 1.500000000 | 1.872885231 |
| 786432 | 2^18 * 3^1 | (16,1), (18,0) | (46,46,46) | 0,1,2 (tie) | 1.500000000 | 1.479810553 |
| 3145728 | 2^20 * 3^1 | (18,1), (20,0) | (55,55,55) | 0,1,2 (tie) | 1.500000000 | 1.973080737 |
| 3188646 | 2^1 * 3^13 | (18,1), (20,0) | (56,55,55) | 1,2 (tie) | 1.520464897 | 2.000000000 |
| 6291456 | 2^21 * 3^1 | (19,1), (21,0) | (60,60,60) | 0,1,2 (tie) | 1.500000000 | 1.315387158 |
| 6377292 | 2^2 * 3^13 | (19,1), (21,0) | (60,61,60) | 0,2 (tie) | 1.520464897 | 1.333333333 |
| 12582912 | 2^22 * 3^1 | (20,1), (22,0) | (65,65,65) | 0,1,2 (tie) | 1.500000000 | 2.630774316 |
| 12754584 | 2^3 * 3^13 | (20,1), (22,0) | (65,65,66) | 0,1 (tie) | 1.520464897 | 2.666666667 |
| 25165824 | 2^23 * 3^1 | (21,1), (23,0) | (71,70,70) | 1,2 (tie) | 1.500000000 | 1.753849544 |
| 25509168 | 2^4 * 3^13 | (21,1), (23,0) | (72,70,70) | 1,2 (tie) | 1.520464897 | 1.777777778 |
| 50331648 | 2^24 * 3^1 | (22,1), (24,0) | (76,76,76) | 0,1,2 (tie) | 1.500000000 | 1.169233029 |
| 51018336 | 2^5 * 3^13 | (22,1), (24,0) | (76,77,76) | 0,2 (tie) | 1.520464897 | 1.185185185 |
| 402653184 | 2^27 * 3^1 | (25,1), (27,0) | (94,94,94) | 0,1,2 (tie) | 1.500000000 | 1.039318248 |
| 408146688 | 2^8 * 3^13 | (25,1), (27,0) | (94,95,94) | 0,2 (tie) | 1.520464897 | 1.053497942 |
| 1610612736 | 2^29 * 3^1 | (27,1), (29,0) | (107,107,107) | 0,1,2 (tie) | 1.500000000 | 1.385757664 |
| 1632586752 | 2^10 * 3^13 | (27,1), (29,0) | (108,107,107) | 1,2 (tie) | 1.520464897 | 1.404663923 |
| 3265173504 | 2^11 * 3^13 | (28,1), (30,0) | (114,114,114) | 0,1,2 (tie) | 1.520464897 | 2.809327846 |
| 6530347008 | 2^12 * 3^13 | (29,1), (31,0) | (121,121,121) | 0,1,2 (tie) | 1.520464897 | 1.872885231 |
| 12884901888 | 2^32 * 3^1 | (30,1), (32,0) | (128,128,128) | 0,1,2 (tie) | 1.500000000 | 1.231784591 |
| 13060694016 | 2^13 * 3^13 | (30,1), (32,0) | (129,128,128) | 1,2 (tie) | 1.520464897 | 1.248590154 |
| 25769803776 | 2^33 * 3^1 | (31,1), (33,0) | (136,135,135) | 1,2 (tie) | 1.500000000 | 2.463569181 |
| 26121388032 | 2^14 * 3^13 | (31,1), (33,0) | (136,136,135) | 2 (unique) | 1.520464897 | 2.497180308 |
| 27518828544 | 2^22 * 3^8 | (31,1), (33,0) | (136,136,136) | 0,1,2 (tie) | 1.601806641 | 2.630774316 |
| 27894275208 | 2^3 * 3^20 | (31,1), (33,0) | (136,137,136) | 0,2 (tie) | 1.623660513 | 2.666666667 |
| 51539607552 | 2^34 * 3^1 | (32,1), (34,0) | (143,143,143) | 0,1,2 (tie) | 1.500000000 | 1.642379454 |
| 52242776064 | 2^15 * 3^13 | (32,1), (34,0) | (143,143,144) | 0,1 (tie) | 1.520464897 | 1.664786872 |
| 103079215104 | 2^35 * 3^1 | (33,1), (35,0) | (151,151,151) | 0,1,2 (tie) | 1.500000000 | 1.094919636 |
| 104485552128 | 2^16 * 3^13 | (33,1), (35,0) | (152,151,151) | 1,2 (tie) | 1.520464897 | 1.109857915 |
| 206158430208 | 2^36 * 3^1 | (34,1), (36,0) | (159,159,159) | 0,1,2 (tie) | 1.500000000 | 2.189839272 |
| 208971104256 | 2^17 * 3^13 | (34,1), (36,0) | (159,160,159) | 0,2 (tie) | 1.520464897 | 2.219715829 |

### A simple interval rule fitting all 507 cutoffs

The following candidate has **zero mismatches on all 507 saved cutoffs**:

```text
E(t) = 1 iff there exists an integer m >= 0 such that
    24*2^m <= t < 27*2^m
    and c_((m+2) mod 3)(t) = min(c_0(t), c_1(t), c_2(t)).
Otherwise E(t) = 0.
```

The intervals are disjoint, so m is unique when one applies. Equivalently,
put k=floor(log2(t)). The condition is k>=4,
3/2 <= t/2^k < 27/16, and c_((k-2) mod 3) is minimal. A tie is allowed,
but the specific colour determined by m must attain the minimum.
The rule identifies all 32 positive cases and all 475 zero cases correctly.
An independent direct enumeration of interval exponents also matched all
507 cutoffs, rather than relying only on the floor-log implementation.

Among the 32 excess cutoffs, 15 have a three-way minimum tie, 16 have
exactly two minimizers, and one has a unique minimum: at t=26121388032,
(c0,c1,c2)=(136,136,135), so colour 2 alone is minimal. Thus a requirement
that the minimum be tied would miss a real discrepancy.

There are only four observed normalized binary ratios among the positive
cases: 3/2 (16 cutoffs), 1594323/1048576 (14 cutoffs), 6561/4096 (one), and
3486784401/2147483648 (one). The ternary ratios range much more widely;
the simple ternary interval tested below does not characterize E.
These counts and ratios are observations on the saved finite domain.

### Why 24 and 27, and which pair is meant

There is a concrete local modification behind the dyadic interval. Let
r=(m+2) mod 3. Start with the omission cover consisting of every
corner-participating point of colour r. Remove these three omissions:

```text
(m+2,0), (m+1,2), (m+3,1)
weights: 4*2^m, 18*2^m, 24*2^m
```

Add these two omissions instead:

```text
(m+1,1), (m+3,0)
weights: 6*2^m, 8*2^m
```

The three removed points have colour r; the two added points have colour
r+1 modulo 3. At t >= 24*2^m, all required points and their relevant
corners are present. Before 27*2^m, every corner losing one of the three
old omissions is still hit by one of the two new omissions. In particular,
the potentially obstructing corner anchored at (m,2) has its third point
(m,3), of weight 27*2^m, outside the domain. Other additional corners of
the removed points have still larger thresholds. Thus the correction
is a cover one smaller than the original colour-r cover.

The program explicitly checked this modification at **all 89 saved
cutoffs in the dyadic intervals**, including the 57 with E=0. When colour
r is minimal, it constructs a corner-free set of size g_cand+1; this
happens at exactly the 32 observed discrepancy cutoffs. Each corrected
cover has cardinality |Σ|-exact_g there, so it is an optimum relative to
the saved exact results. The complete corrected covers, not just the
pair coordinates, are saved in `experiments/excess-results.json`.

This construction gives a general ordinary mathematical **sufficiency**
argument for an improvement of at least one when the stated condition
holds. The assertion that E is exactly one there, and that E is zero
everywhere else, is only verified on the 507 cutoffs. No general upper
bound or necessity theorem has been established, and no Lean was written.

### Verification that the pair is omitted in every optimum

The listed pair is more than a choice in one saved witness: both points
belong to no maximum corner-free set at every one of the 32 cutoffs.
For the first ten cutoffs, the 20 existing exact point-requirement
classifications already show this. For the other 22 cutoffs,
`experiments/verify_excess_pairs.py` made **44 fresh exact MaxSAT queries**,
one requiring each point. All queries closed their integer objective
bounds, checked the requirement and cover witnesses, and found the
required maximum to be exactly g-1. The unrestricted saved optimum
witnesses omit both points, witnessing exclusion at size g.

All 64 pair points are therefore classified `none`, with no counterexamples.
The new query bounds, omission witnesses, timings and source attribution
are saved in `experiments/excess-pairs.json`. This settles the pairs at
the 22 cutoffs that lacked membership data in the previous notes; full
membership classifications of all other vertices were not recomputed.
Since the constructed optimum contains every point outside colour r
except this pair, no other off-colour point can belong to `none` at these
cutoffs. The pair is exactly the off-colour `none` set relative to r.
Different optima can make additional off-colour omissions, so the pair
should not be extracted by treating every saved witness as canonical.

### All tested rules and every mismatch

A false positive predicts E=1 when E=0; a false negative predicts E=0
when E=1. All five tests used all 507 cutoffs. Full per-cutoff predictions
and every mismatch (with counts and actual/predicted E) are in
`experiments/excess-results.json`; the cutoff lists below are complete.

| Rule | Correct E=1 cases | False positives | False negatives | Total mismatches |
| --- | ---: | ---: | ---: | ---: |
| D: some 24*2^m <= t < 27*2^m, m>=0 | 32 | 57 | 0 | 57 |
| D and at least two minimizing colours | 31 | 8 | 1 | 9 |
| D and c0=c1=c2 | 15 | 0 | 17 | 17 |
| D and colour (m+2) mod 3 minimal | 32 | 0 | 0 | 0 |
| Some 10*3^j <= t < 12*3^j, j>=0 | 5 | 61 | 27 | 88 |

D: some 24*2^m <= t < 27*2^m, m>=0:

False positives: 24, 48, 96, 192, 384, 768, 3072, 6561, 13122, 24576, 26244, 49152, 52488, 98304, 104976, 196608, 209952, 393216, 419904, 839808, 1572864, 1594323, 1679616, 3359232, 6718464, 13436928, 26873856, 53747712, 100663296, 102036672, 107495424, 201326592, 204073344, 214990848, 429981696, 805306368, 816293376, 859963392, 1719926784, 3221225472, 3439853568, 3486784401, 6442450944, 6879707136, 6973568802, 13759414272, 13947137604, 55037657088, 55788550416, 110075314176, 111577100832, 220150628352, 223154201664, 412316860416, 417942208512, 440301256704, 446308403328.

False negatives: none.


D and at least two minimizing colours:

False positives: 192, 384, 839808, 1572864, 805306368, 3439853568, 6879707136, 412316860416.

False negatives: 26121388032.


D and c0=c1=c2:

False positives: none.

False negatives: 6144, 12288, 3188646, 6377292, 12754584, 25165824, 25509168, 51018336, 408146688, 1632586752, 13060694016, 25769803776, 26121388032, 27894275208, 52242776064, 104485552128, 208971104256.


D and colour (m+2) mod 3 minimal:

False positives: none.

False negatives: none.


Some 10*3^j <= t < 12*3^j, j>=0:

False positives: 32, 96, 288, 864, 2592, 7776, 8192, 23328, 24576, 69984, 73728, 209952, 221184, 629856, 663552, 1889568, 1990656, 2097152, 5668704, 5971968, 16777216, 17006112, 17915904, 18874368, 53747712, 56623104, 150994944, 153055008, 161243136, 169869312, 452984832, 459165024, 483729408, 509607936, 1358954496, 1377495072, 1451188224, 1528823808, 4076863488, 4132485216, 4294967296, 4353564672, 4586471424, 12230590464, 12397455648, 13759414272, 36691771392, 37192366944, 38654705664, 39182082048, 41278242816, 110075314176, 111577100832, 115964116992, 117546246144, 123834728448, 330225942528, 334731302496, 347892350976, 352638738432, 371504185344.

False negatives: 1536, 6144, 12288, 786432, 3145728, 3188646, 6377292, 12582912, 12754584, 25165824, 25509168, 402653184, 408146688, 1610612736, 1632586752, 3265173504, 6530347008, 25769803776, 26121388032, 27518828544, 27894275208, 51539607552, 52242776064, 103079215104, 104485552128, 206158430208, 208971104256.

### Commands, artifacts and remaining work

```bash
python3 experiments/excess_rule.py
/tmp/erdos168-venv/bin/python experiments/verify_excess_pairs.py
```

- `experiments/excess-results.csv`: the complete 32-row enriched table,
  including exact rational ratios and pair weights.
- `experiments/excess-results.md`: the readable table displayed above.
- `experiments/excess-results.json`: all 507 comparisons, every rule's
  predictions/mismatches, exact ratios, and corrected optimum witnesses.
- `experiments/excess-pairs.json`: 44 new requirement queries and 20
  reused classifications verifying the pair points belong to no optimum.
- `experiments/excess_rule.py` uses only the Python standard library;
  the verification script reuses the existing independent Z3 solver.

The factorizations, floor-power inequalities, exact ratios, corrected
optimum sizes and pair records were cross-checked. The CSV and displayed
Markdown tables agree with the JSON; every discrepancy cutoff is present,
including all four beyond 10^11. `git diff --check` passed. All theorem
statements and Lean files are unchanged, and no wallet, key or secret
file was accessed. The new interval rule is a candidate for a general
exact formula; proving its necessity and optimality remains separate
from the irrationality argument. Neither has been proved in Lean.

## Holdout experiment: predictions frozen through 10^14

The rule from commit `6ca0694` is now frozen before comparing new exact
answers. `experiments/holdout_predictions.py` predicts

```text
g_pred(t) = |Σ(t)| - min_j c_j(t) + E_pred(t),
E_pred(t) = 1 iff some m>=0 satisfies 24*2^m <= t < 27*2^m
                and c_((m+2) mod 3)(t) = min_j c_j(t).
```

There are **720 smooth cutoffs through 10^14**, ending at
`96402615118848`. The rule predicts **481 jumps**, including 142 beyond
the original 507-prefix sample, and predicts g(10^14)=481. Every predicted
increment is zero or one. The complete predicted jump set is saved in
`experiments/predicted-1e14-jumps.txt`; JSON and CSV retain every cutoff,
factorization, participating-colour count, predicted excess and g.
All old 507 exact values agree with the reconstructed prediction.
Every predicted size has an independently checked feasible cover, which
establishes achievability but does not establish optimality.

The frozen holdout plan contains **213 new cutoffs**, all above
`470184984576`. It prioritizes all **13 predicted E=1 cases** (larger m
first), then the **42 distinct new smooth cutoffs** immediately below,
at and above the two window edges, then a reproducible sample of 25
other cutoffs (seed `16820261004`), and finally every remaining cutoff.
The selection and predictions are saved before the holdout solver run.

```bash
python3 experiments/holdout_predictions.py
python3 -m py_compile experiments/holdout_predictions.py experiments/holdout_worker.py experiments/holdout_verify.py
/tmp/erdos168-venv/bin/python experiments/holdout_verify.py --timeout-ms 10000
```

Each exact query runs in a separate process, receives only t and resource
limits, and builds the unrestricted corner-cover optimization problem;
it receives no prediction, proposed optimum, colour rule, or bound.
The parent compares results only after the integer optimum bounds close
and the omission witness passes the existing numerical-corner checks.
The initial standalone query at `57127475625984` did not close within
30 seconds; UNKNOWN is not an optimum or a counterexample. A ten-second
per-query holdout run is underway. Completed exact answers so far include
g(`847288609443`)=354 and g(`52776558133248`)=463, both agreeing with the
predicted excess. The complete results and limitations will be recorded
when that run finishes, with additional solver work if needed.

Memory is measured using each worker's `/proc/self/status` `VmHWM`.
The initial raw `getrusage` figure of about 510 MiB retained earlier
process history, as shown by a small worker with raw 510 MiB but current
image peak 51.7 MiB; that raw figure is unsuitable for this report.
Both counters are retained in query records, but summaries use `VmHWM`.
The current workers have a 1024 MiB virtual address-space limit; timeouts
so far have not reached that limit. No Lean was written or changed.

### Additional exact backend

To resolve the MaxSAT timeouts I wrote
`experiments/holdout_cpsat_worker.py`, an independent formulation using
[Google OR-Tools CP-SAT](https://developers.google.com/optimization/cp/cp_solver).
It uses the same mathematical corner-cover problem, with one Boolean
omission variable for each smooth integer, one hard disjunction for each
numerical triple, and an unrestricted minimum-cardinality objective.
There are no colour restrictions, supplied objective bounds or predicted
solutions. It requires `OPTIMAL`, equality of both reported objective
values with the small integer cover cardinality (without rounding), and
a separately reconstructed numerical-corner witness check. `FEASIBLE`
and `UNKNOWN` are not treated as exact answers. This is trusted solver
computation, not an independently certified proof or a Lean proof.

OR-Tools version `9.15.6755` is pinned in
`experiments/requirements-holdout.txt`. Its
[licence is Apache 2.0](https://github.com/google/or-tools/blob/stable/LICENSE).
The problem-specific code is original; no DP or published proof code
was copied. Installation occurred only in the existing temporary venv:

```bash
/tmp/erdos168-venv/bin/python -m pip install ortools==9.15.6755
/tmp/erdos168-venv/bin/python experiments/validate_cpsat.py
python3 experiments/holdout_verify.py --backend cp_sat --timeout-ms 30000 --wall-budget-seconds 1800 --output experiments/holdout-cpsat.json
```

Pip was bootstrapped there from a public wheel after checking SHA-256
`71138adf1f4ca900cdb7d289c21b7494329f2332b6d85f0e1c42108c0384ed3e`.
The backend validation agrees with exhaustive subset enumeration at all
64 integer cutoffs 1..64 and with six saved MaxSAT optima, including the
first excess case 1536, the unique-minimum case `26121388032`, an upper
window edge, and the original final cutoff. The one-worker trial at
`26121388032` timed out after 30 seconds without an exact result; the
four-worker validation closed it and agreed. This was a timeout, not a
different value. All 70 accepted comparisons are saved in
`experiments/cpsat-validation.json`.

The holdout backend uses four search workers, seed 168 and the same
1024 MiB address-space cap. All **13 new predicted-excess cutoffs** have
now closed their unrestricted exact objectives and match the frozen
rule, including every m=41 excess case. The remaining holdout run is
still in progress; complete results will be recorded below.

### Prioritized holdouts and the first timeout retry

All 13 new predicted-positive cases have exact E=1, as listed here.
Both g and E were compared only after unrestricted optimization closed.

| t | Factorization | m | (c0,c1,c2) | Exact g |
| ---: | --- | ---: | --- | ---: |
| 847288609443 | 2^0 * 3^25 | 35 | (177, 176, 176) | 354 |
| 1694577218886 | 2^1 * 3^25 | 36 | (185, 185, 185) | 371 |
| 3389154437772 | 2^2 * 3^25 | 37 | (194, 194, 194) | 389 |
| 6778308875544 | 2^3 * 3^25 | 38 | (203, 203, 203) | 407 |
| 13374150672384 | 2^23 * 3^13 | 39 | (212, 212, 212) | 425 |
| 13556617751088 | 2^4 * 3^25 | 39 | (213, 212, 212) | 426 |
| 14281868906496 | 2^12 * 3^20 | 39 | (213, 213, 213) | 427 |
| 27113235502176 | 2^5 * 3^25 | 40 | (222, 222, 222) | 445 |
| 52776558133248 | 2^44 * 3^1 | 41 | (231, 231, 231) | 463 |
| 53496602689536 | 2^25 * 3^13 | 41 | (232, 231, 231) | 464 |
| 54226471004352 | 2^6 * 3^25 | 41 | (232, 231, 232) | 465 |
| 56358560858112 | 2^33 * 3^8 | 41 | (232, 232, 232) | 465 |
| 57127475625984 | 2^14 * 3^20 | 41 | (233, 232, 232) | 466 |

All 42 distinct new smooth neighbors immediately below, at and above
`24*2^m` and `27*2^m`, and all 25 cutoffs in the frozen random sample,
have now also been solved exactly and agree. Positive excess does not
mean that the cutoff itself is a jump: `56358560858112` has g=465,
the same as its preceding smooth cutoff `54226471004352`.

At random cutoff `11132555231232`, the initial four-worker CP-SAT run
returned only `FEASIBLE` after 30 seconds (incumbent g=419, minimum-cover
lower bound 208). It was not accepted. A fresh unrestricted eight-worker
run closed both omission bounds at 208 and gave **g=420**, matching the
rule, in 11.862 seconds including process startup. Its peak resident
memory was 196840 KiB = 192.23 MiB. This was an incomplete search followed
by an exact result, not a mismatch. The retry receives no proposed bound.

```bash
python3 experiments/holdout_verify.py --backend cp_sat --workers 8 --timeout-ms 120000 --wall-budget-seconds 180 --only-t 11132555231232 --output experiments/holdout-cpsat-retry.json
```

The retry bounds, witness and resources are in
`experiments/holdout-cpsat-retry.json` and `.csv`. The remaining 213-prefix
coverage run continues; no general formula or Lean theorem is claimed.

### Completed holdout results through 10^14

**Every one of the 213 new cutoffs now has an unrestricted exact solver
answer. There are zero mismatches and no unverified cutoffs.** The rule
was unchanged from `6ca0694` throughout the experiment. Combining these
answers with the original 507 gives all **720 smooth cutoffs through
10^14**. The original fitting file `experiments/results.json` remains
unchanged; the extended exact data is saved separately.

| Holdout cohort | Cutoffs selected | Exact answers | Mismatches |
| --- | ---: | ---: | ---: |
| Predicted E=1, m=35..41 | 13 | 13 | 0 |
| Smooth cutoff immediately below, at and above both window edges | 42 | 42 | 0 |
| Other cutoffs sampled with seed 16820261004 | 25 | 25 | 0 |
| Entire new domain above 470184984576 | 213 | 213 | 0 |

The cohorts overlap. The full new domain has 13 exact E=1 cases, listed
above, and 200 exact E=0 cases. Across all 720 cutoffs there are 45 E=1
cases and 675 E=0 cases; no excess is larger than one. Exact g is never
below the achievable colour candidate or the frozen prediction.
The complete mismatch list is **empty**.

There are **481 exact jumps**, including **142 new jumps** after the
original sample. The predicted and exact jump sets agree at every
smooth cutoff, and all exact increments are zero or one. The largest
cutoff actually solved is

```text
t = 96402615118848 = 2^10 * 3^23,
|Σ(t)| = 720, (c0,c1,c2) = (240,239,240), E(t) = 0,
minimum omissions = 239, g(t) = 481.
```

This is also g(10^14), since there is no further smooth number between
this cutoff and 10^14. The complete predicted list, generated before
the new comparisons, is `experiments/predicted-1e14-jumps.txt`; the
independently solved list is `experiments/verified-1e14-jumps.txt`.

### Solver limits, memory and the second retry

| Run | Attempted | Exact answers | Unclosed queries | Largest exact cutoff | Peak worker RSS |
| --- | ---: | ---: | ---: | ---: | ---: |
| Z3 rc2, 10-second query cap | 209 | 56 | 153 | 81339706506528 | 109.14 MiB |
| CP-SAT, 4 workers, 30-second query cap | 213 | 211 | 2 | 96402615118848 | 196.38 MiB |
| CP-SAT retry, 8 workers, 120-second query cap | 1 | 1 | 0 | 11132555231232 | 192.23 MiB |
| CP-SAT final retry, 8 workers, 120-second query cap | 1 | 1 | 0 | 91507169819844 | 209.69 MiB |

The Z3 pass stopped at its 1800-second overall budget after finishing
its current query (1810.130 seconds total). Four planned cutoffs were
not attempted by that pass; all four were solved by CP-SAT. The main
CP-SAT pass took 1148.041 seconds, about 19.1 minutes. All **56** new
cutoffs closed by both solvers have identical g. The full Z3 timeout
and unattempted lists are retained in `experiments/holdout-z3.json`;
they are performance results, not mathematical mismatches.

The second CP-SAT timeout was at
`91507169819844 = 2^2 * 3^28`. After 30 seconds the four-worker query
had only a feasible g=471 and an omission lower bound of 237. Neither
was accepted as exact. A fresh unrestricted eight-worker query closed
the omission bounds at **239**, giving **g=479**, in **9.715 seconds**
including startup, matching the frozen prediction. Its checked cover,
bounds, statuses and memory are in
`experiments/holdout-cpsat-retry-large.json` and `.csv`.

Every worker had a 1024 MiB virtual address-space limit. No query hit
that cap or reported an out-of-memory failure. Resident memory summaries
use the current worker memory-image `VmHWM`, not the inherited raw
`getrusage` counter discussed above. The largest measured worker peak
was **214720 KiB = 209.6875 MiB**. The solver reached every requested
cutoff; no inability to reach 10^14 remains.

A column-by-column bitmask DP was considered as an alternative. The
largest column at 10^14 has 30 points, so an uncompressed implementation
has 2^30 masks. Two full maximum-height 16-bit cost arrays would alone
use 4 GiB, before other data or transition work. This is an estimate
for that simple storage layout, not a lower bound for all possible DPs;
sparse or compressed states could improve it. I did not implement it
because the independently written CP-SAT backend reached all 720
prefixes with much smaller measured memory. No user DP code was copied.

### Reproduction and independent result checks

```bash
python3 experiments/holdout_predictions.py
python3 experiments/holdout_verify.py --timeout-ms 10000
python3 experiments/holdout_verify.py --backend cp_sat --timeout-ms 30000 --wall-budget-seconds 1800 --output experiments/holdout-cpsat.json
python3 experiments/holdout_verify.py --backend cp_sat --workers 8 --timeout-ms 120000 --wall-budget-seconds 180 --only-t 11132555231232 --output experiments/holdout-cpsat-retry.json
python3 experiments/holdout_verify.py --backend cp_sat --workers 8 --timeout-ms 120000 --wall-budget-seconds 180 --only-t 91507169819844 --output experiments/holdout-cpsat-retry-large.json
python3 experiments/holdout_results.py
```

The verification commands above use this environment's temporary solver
venv by default; `--python experiments/.venv/bin/python` selects a local
installation of `experiments/requirements-holdout.txt` instead.

- `experiments/holdout-results.csv`: all 213 new cutoffs with factors,
  colours, candidate, prediction, exact g/E, exact/predicted increments,
  priority tags and the exact solvers that closed them. Its `difference`
  column means **exact g minus predicted g**, and is zero in every row.
- `experiments/holdout-results.json`: the same comparisons, complete
  mismatch list, cohort counts and SHA-256 provenance for every source.
- `experiments/results-1e14.json`: all 720 exact optima, matching integer
  bounds and omission witnesses, with the actual jump set and provenance.
- `experiments/results-1e14.csv`: all 720 comparisons. Here `difference`
  means **exact g minus g_cand**; `prediction_difference` means exact g
  minus g_pred. The latter is zero throughout.
- The four raw solver JSON/CSV reports preserve incomplete searches,
  accepted bounds, witnesses, query times, resource caps and memory.

`holdout_results.py` rechecked every accepted query's cover, cardinality
and bounds, rejected cross-solver disagreements, and independently
reconstructed coordinate and numerical corners and participating-colour
counts at all 720 prefixes. It checked the frozen rule and fitting-file
hashes, the one-point increment bound, and exact equality of the full
predicted and solved jump sets. An attempted aggregation before the last
retry correctly refused to produce a complete report with one missing
exact answer. Python compilation and `git diff --check` passed.

The staged whitespace check then caught the standard CSV writer's CRLF
line endings in new tables; the earlier unstaged check had not inspected
new files. I let that commit proceed despite the failed staged check.
The writers now explicitly emit LF endings, and all seven CSV files
created in this task were normalized without changing any data fields.
The staged check and the complete task diff from `6ca0694` were checked
again before committing this correction; both passed.

These holdouts substantially extend the tested domain, but a proof of
the exact formula for all t and the irrationality of the resulting
infinite series are still open tasks. No Lean was written or changed,
and no wallet or key file was accessed.

## Density expansion from the frozen rule (2026-10-05)

This investigation concerns the density of the rule frozen at `6ca0694`.
It is conditional on that rule being the exact g formula for all cutoffs;
the rule has only been checked by unrestricted solvers through 10^14.
Nothing here is a Lean proof or an irrationality argument.

### Exact contribution at a newly added smooth number

Write h(t)=min_j c_j(t). If s=2^a*3^b is the new lattice point, the
new participating-colour counts are as follows:

| New point | Newly participating points | Count increment |
| --- | --- | --- |
| b=0 | none | (0,0,0) |
| (a,b)=(0,1), s=3 | (0,0), (1,0), (0,1) | (1,1,1) |
| b=1, a>=1 | (a,1), (a+1,0) | +1 in colours a-1 and a+1 modulo 3 |
| b>=2 | (a,b) | +1 in colour a-b modulo 3 |

All points with b>=1 participate immediately. A point (a,0), a>=1,
first participates at 3*2^(a-1); (0,0) first participates at 3.
This gives an independent incremental count formula. It matches all
720 saved exact prefixes and all independently reconstructed colour
counts, without calling the old prediction program or an optimizer.

Put Δh(s)=h(s)-h(s^-), ΔE(s)=E(s)-E(s^-). The rule's jump indicator
is J(s)=1-Δh(s)+ΔE(s), hence

```text
L_rule = 1 - H/3 + W/3,
H = sum_s Δh(s)/s,     W = sum_s ΔE(s)/s.
```

The subtracted term is the **increase** in the minimum colour count;
h never decreases. The constant 1 uses sum_s 1/s=3 exactly.
Each Δh is 0 or 1. J is also always 0 or 1: an interior E increase
requires Δh=1, an interior E decrease requires Δh=0; at the lower
edge the two born colours enforce the same restriction, while at the
upper edge the unchanged relevant minimal colour enforces Δh=0 if E
was positive. Powers of two introduce no participating-count change.

### A valid regrouping with bounded rational coefficients

Pair exponents a=2u and a=2u+1, and group by n=u+b. Define

```text
C_n = sum_(b=0..n) (2*Δh(2^(2(n-b))*3^b)
                         + Δh(2^(2(n-b)+1)*3^b)) * (3/4)^(n-b).
```

Then H=(1/2)*sum_n C_n/3^n and 0<=C_n<=12. This is a diagonal
grouping whose endpoints have weights 3^n and 4^n (or twice those).

For each dyadic window, let
W_m=sum of ΔE(s)/s over its changes, including its upper-edge exit.
Equivalently it is the sum of 1/start-1/end over positive episodes.
Therefore

```text
0 <= W_m <= 1/(24*2^m) - 1/(27*2^m) = 1/(216*2^m),
U_k = 4^k * (W_(2k) + W_(2k+1)),    0 <= U_k <= 1/144.
```

This produces the exact, absolutely convergent identity

```text
L_rule = (1/6) * (6 + sum_k alpha_k/4^k + sum_k beta_k/3^k),
alpha_k = 2*U_k,        beta_k = -C_k,
0 <= alpha_k <= 1/72,  -12 <= beta_k <= 0.
```

These coefficients are **rational**, not the requested integers.
For example (alpha_4,beta_4)=(139/17496,-305/64). The least common
scale N that would make these particular natural coefficients integers
through k=40 is 2^79*3^55. Through k=160 it increases to 2^318*3^204.
These finite checks do not prove that no different regrouping can
produce bounded integer coefficients.

The window is not a single positive episode in every case. At m=39,
E changes at 13374150672384 (+1), 14089640214528 (-1),
14281868906496 (+1), and 14843406974976 (-1). Every event and colour
count through 54*4^40 is saved in `experiments/density-window-events.csv`;
`experiments/density-contributions.csv` records every smooth cutoff.

### Numerical check and an integer endpoint trial

The rational series through k=40 is

```text
0.80096575500655898913344222942366676214690844605842...
```

Its exact signed-tail enclosure is

```text
[partial - 3^(-40), partial + 1/(1296*4^40)].
```

An independent direct jump sum through 54*4^160 gives
0.80096575500655898909042032638808241322472498911028...;
the remaining all-smooth reciprocal mass bounds its error. The exact
intervals intersect and certify much more than twelve decimal places
for the density of the frozen rule.

The quoted 0.8009657550 is a ten-decimal rounding, not an exact value.
The rule's twelve-decimal rounding is **0.800965755007**. Independently
of extending the rule, the existing 720 exact prefixes give the actual
density enclosure

```text
[0.80096575500645906403407966569563013853263570518260...,
 0.80096575500661058219658788202477788045293946639215...].
```

Thus literal agreement with 0.800965755000 to an absolute tolerance
of 10^(-12) is impossible; the already verified lower bound exceeds it
by more than 6.459*10^(-12). The saved solver interval certifies ten
places, but straddles the twelve-place rounding boundary. The additional
digits calculated here remain conditional on the frozen rule.

For an integer endpoint trial, group the *net* loss Δh-ΔE on the same
diagonals. The finite numerator P_n is an integer with denominator
4^n*3^n. Solve P_n=A_n*3^n+B_n*4^n, choosing A_n in
[-4^n/2,4^n/2) to minimize its absolute value, and set
a_n=-A_n, b_n=-B_n. This gives exact **paired finite summands** with
N=6, c=6. Already (a_4,b_4)=(124,-44); through 40 the largest absolute
values are 487325319037653169772096 and 4900828572324321976.
The coefficients become enormous and their normalized summands cancel.
Boundedness and convergence of the two separate infinite integer
series have not been established; splitting the convergent paired
sum into them would be unjustified. This trial is not a claimed answer
to the requested bounded-integer formula.

`experiments/density-expansion.csv` and JSON retain all 41 coefficient
rows, exact candidate ratios, rational coefficients and integer trials.
The report records every conflict with the small geometric ratio-band
catalog and a longer 160-index audit. The completed nearest-power
refinement is recorded below.

```bash
python3 experiments/density_expansion.py
```

The new program uses only the standard library and exact fractions.
It rechecks the frozen source hash and the saved solver/count data.
The original rule, exact-result files and all Lean files are unchanged.

### Nearest-power grouping and the average-colour constant

Let P(t)=c_0(t)+c_1(t)+c_2(t), the number of participating points,
and let d(t)=P(t)-3h(t). The birth table above gives
Δd=ΔP-3Δh, always an integer between -2 and 2. In particular:

- At a pure power of two, Δd=0.
- At s=3, Δd=0.
- At b=1,a>=1, Δd is 2 if Δh=0 and -1 if Δh=1.
- At b>=2, Δd is 1 if Δh=0 and -2 if Δh=1.

The total weighted participation increment has an exact rational value:

```text
sum_s ΔP(s)/s
  = sum_(a>=0,b>=1) 1/(2^a*3^b)
    + 1/3 + sum_(a>=1) 1/(3*2^(a-1))
  = 1 + 1/3 + 2/3 = 2.
```

Consequently H=(2-sum_s Δd(s)/s)/3, so the average-colour part
contributes 7/9 to the density:

```text
L_rule = 7/9 + (1/9)*sum_s Δd(s)/s + (1/3)*sum_s ΔE(s)/s.
```

Now group a smooth number with the immediately preceding pure power
of three. Define

```text
B_k = 3^k * sum_(3^k <= s < 3^(k+1)) Δd(s)/s,
U_k = 4^k * (W_(2k)+W_(2k+1)), as above.

L_rule = (1/9) * (7 + sum_k a_k/4^k + sum_k b_k/3^k),
a_k = 3*U_k,   b_k = B_k.
```

This is an exact nearest-power identity, but its displayed a_k,b_k
are **rational coefficients**, not a solution of the requested
bounded-integer problem. We have 0<=a_k<=1/48. Absolute convergence
of the b series follows from |Δd|<=2 and the all-smooth reciprocal
sum; no uniform bound on b_k has been proved. In the 0..160 audit
the largest |b_k| is 718505744573433/281474976710656, about
2.552645187043. The least scale N clearing the actual coefficients
a_k/9,b_k/9 through 40 is 2^63*3^55, and through 160 is
2^252*3^204. These are finite necessary scales for this grouping,
not universal impossibility results for other identities.

Subtracting the average participation term is necessary if this direct
grouping is to have bounded colour coefficients. The raw coefficients
R_k=2*3^k*sum_(3^k<=s<3^(k+1)) Δh(s)/s cannot be uniformly
bounded: each is at least 2/3 times the number of h increases in its
block. Bounded R_k would imply h(3^K)=O(K). On the other hand,
the lattice contains a rectangle with a<=floor(K*log_2(3)/2)
and 1<=b<=floor(K/2); all its points participate and each colour
occupies a third of each long row up to a bounded error. Thus every
c_j(3^K), and hence h(3^K), is Ω(K^2). The audit's largest raw
R_k is about 104.1721886. This observation concerns the raw nearest
grouping, not every possible bounded-integer representation.

The complete nearest-power rational coefficient table is:

| k | a_k (N=9, rational) | b_k (N=9, rational) |
| --- | --- | --- |
| 0 | 0 | 0 |
| 1 | 0 | 1 |
| 2 | 0 | -3/4 |
| 3 | 1/72 | -3/4 |
| 4 | 139/11664 | -51/64 |
| 5 | 0 | -87/128 |
| 6 | 0 | -267/512 |
| 7 | 139/34992 | -2037/2048 |
| 8 | 139/34992 | -1767/4096 |
| 9 | 139/11664 | 14367/8192 |
| 10 | 139/11664 | -1803/2048 |
| 11 | 0 | -4215/65536 |
| 12 | 139/17496 | 691635/524288 |
| 13 | 47089/4251528 | 647709/1048576 |
| 14 | 87025/8503056 | -4620261/4194304 |
| 15 | 625/34992 | 10001091/8388608 |
| 16 | 139/11664 | 2912325/4194304 |
| 17 | 649928320/282429536481 | -35603961/33554432 |
| 18 | 649928320/94143178827 | 370798827/268435456 |
| 19 | 5602197223/564859072962 | 280144833/1073741824 |
| 20 | 52178765849/4518872583696 | 621701355/2147483648 |
| 21 | 36580486169/2259436291848 | 2763582273/8589934592 |
| 22 | 649928320/94143178827 | 2716181421/17179869184 |
| 23 | 0 | 13566575373/68719476736 |
| 24 | 4581153284461/617673396283947 | 9098004699/8589934592 |
| 25 | 4581153284461/411782264189298 | -796655795343/549755813888 |
| 26 | 4581153284461/411782264189298 | -1737753915957/2199023255552 |
| 27 | 13902108371950217/1200757082375992968 | 4075892566785/4398046511104 |
| 28 | 122887604273152/50031545098999707 | -27292674275445/17592186044416 |
| 29 | 122887604273152/150094635296999121 | -36935854397367/35184372088832 |
| 30 | 122887604273152/50031545098999707 | 15296539556025/17592186044416 |
| 31 | 16851410874505865/2401514164751985936 | -131664584917743/140737488355328 |
| 32 | 33490101420557792123/5252111478312593242032 | -718505744573433/281474976710656 |
| 33 | 27039976847468589947/2626055739156296621016 | -724528054530399/4503599627370496 |
| 34 | 122887604273152/50031545098999707 | -8699411899018293/9007199254740992 |
| 35 | 122887604273152/50031545098999707 | -91197719718596439/36028797018963968 |
| 36 | 27039976847468589947/2626055739156296621016 | -87324373645778355/144115188075855872 |
| 37 | 24889935323105522555/1750703826104197747344 | -93202684155026463/144115188075855872 |
| 38 | 24889935323105522555/1750703826104197747344 | -267334565829322371/576460752303423488 |
| 39 | 27039976847468589947/2626055739156296621016 | -225746581809115131/576460752303423488 |
| 40 | 121070277808535247848320/19383245667680019896796723 | -4232005989494681379/9223372036854775808 |

The exact nearest-power sum through 40 is

```text
0.80096575500655898909202224667897956586529631381390...
```

Put M_K=3-sum_(s<3^(K+1)) 1/s. A rigorous enclosure is

```text
[partial - (2/9)*M_K,
 partial + (2/9)*M_K + 1/(1296*4^K)].
```

At K=40 this is

```text
[0.80096575500655898871244713045314595356901390416125...,
 0.80096575500655898947159736354306982365002600345991...].
```

It contains the independent direct jump sum quoted above and has width
less than 7.60*10^(-19). Thus both regroupings reproduce the density
of the rule to at least twelve places, with exact tail bounds.

### Ratio thresholds tested, and why this does not solve the requested form

For R4=4^k/3^floor(log_3(4^k)), the geometric thresholds tested are

```text
1, 9/8, 3/2, 27/16, 3.
```

They arise by comparing the four window edges 24*4^k,27*4^k,
48*4^k,54*4^k with their nearest powers of three: 24R4 crosses
27 at 9/8, 48R4 crosses 81 at 27/16, and 54R4 crosses 81 at
3/2. For R3=3^k/4^floor(log_4(3^k)), the tested catalog is

```text
1, 3/2, 27/16, 3, 27/8, 4.
```

A pure power 3^k is in an even window when
3/2<=R3<27/16 and an odd window when 3<=R3<27/8, subject to
m>=0. These thresholds determine geometric window membership;
they do not supply the extra minimum-colour condition or determine
the coefficient sums over the whole block.

Using the first observed value in each band as its proposed constant,
the nearest-power a coefficients have 33 conflicts through 40 and
150 through 160. The b coefficients have 35 and 155 conflicts,
respectively. These are counts of unequal coefficients within bands,
not mismatches in g. Examples away from the initial cutoffs:

| Coefficient | Common ratio interval | First index, ratio, value | Second index, ratio, value |
| --- | --- | --- | --- |
| a | [27/16,3) | k=14, 268435456/129140163, 87025/8503056 | k=15, 1073741824/387420489, 625/34992 |
| b | [27/16,3) | k=12, 531441/262144, 691635/524288 | k=16, 43046721/16777216, 2912325/4194304 |

Even allowing arbitrary interval edges fitted to the finite sample,
the nearest rational a values require at least 39 constant intervals
for indices 0..40 and 160 for 0..160; b requires 41 and 161.
The same counts occur for the alternative bounded rational grouping.
All conflicts, ratios, coefficient fractions and integer endpoint trials
are saved in `experiments/density-expansion.json`; the 41-row CSV
contains indices 0..40, and `density-expansion-audit.csv` contains
the complete 161-row audit. The contribution table also records ΔP,
d and Δd at every smooth cutoff through 54*4^40.

**Result:** neither natural grouping gives bounded integer coefficients
determined by these small ratio catalogs. The diagonal grouping gives
bounded rational coefficients; the nearest-power grouping gives the
rational N=9 identity and the constant 7. The integer endpoint trial
requires very large cancelling coefficients. A different identity with
bounded integers and different thresholds remains possible, but has
not been derived or numerically established. None of these finite
tests proves universal nonexistence of such an identity. A proof of
the frozen g rule and a valid irrationality argument are still needed.

Validation for this step:

```bash
python3 experiments/density_expansion.py
python3 -m py_compile experiments/density_expansion.py
git diff --check
git diff --cached --check
```

The program uses exact Fraction arithmetic, independently generates
the participating-count births, checks the saved optimum/count data
at all 720 solver cutoffs, verifies both regroupings and every integer
paired-summand identity, and checks that the rational-series,
nearest-power, paired-series and direct-smooth enclosures intersect.
It records the frozen-rule, exact-data and program source hashes.
All calculations beyond the solver domain use the frozen rule without
presenting it as proved. No Lean, wallet or key file was accessed or
changed in this density step.

## Round 1: exact row structure of the colour imbalance (2026-10-05)

This round uses no Lean. The identities for participating colours below
follow from the definition of a complete corner, independently of the
frozen g rule. Their use in the density identity, and all comparisons
with g outside the 720 solver cutoffs, remain conditional on that rule.

### Proved row formula and boundary corrections

Put N_b=A_b+1 for an existing row, and write N=3q+r, 0<=r<3.
Let e_j be the j-th unit vector, with subscripts reduced modulo 3, and
define

```text
Q(N,b) = q*(1,1,1) + sum_(0<=i<r) e_(i-b).
```

Every point (a,b) with b>=1 participates immediately: it is the upper
vertex of the complete corner based at (a,b-1), whose other vertices
have weights s/3 and 2s/3 when s=2^a*3^b. Thus r_b=Q(N_b,b) for
**all b>=1**, including b=1. For row 0, (0,0) first participates at
3. For a>=1, the earliest possible corner contains (a,0) as its
right vertex and has largest weight 3*2^(a-1); its use as the left
vertex would require the larger weight 3*2^a. Therefore, for t>=3,
row 0 consists of the participating indices 0<=a<=A_1+1:

```text
r_0(t)=Q(N_1+1,0),    r_1(t)=Q(N_1,1),
r_b(t)=Q(N_b,b) for 2<=b<=B=floor(log_3 t).
```

Equivalently the correction to the full lattice row 0 is
r_0=Q(A_0+1,0)-[A_0=A_1+2]*e_(A_0 mod 3): since
A_0-A_1 is 1 or 2, at most its last point is isolated. Row 1 has
zero correction to Q(A_1+1,1); its exceptional first birth also
activates (0,0), in addition to (1,0), in row 0.

For t<3 all participating counts vanish. The apparent special rule for
b=1 in the birth table is precisely the simultaneous activation of
its own point and the new point in row 0; it does not remove a point
from row 1. Claude's per-row hypothesis is therefore true. Full
triples only change the common colour count and cancel from D.

Define v_0=(1,0), v_1=(-1,1), v_2=(0,-1), and
F(a,b)=sum_(0<=i<(a+1) mod 3) v_(i-b). Its full table is:

| A_b mod 3 | b mod 3 = 0 | b mod 3 = 1 | b mod 3 = 2 |
| --- | --- | --- | --- |
| 0 | (1,0) | (0,-1) | (-1,1) |
| 1 | (0,1) | (1,-1) | (-1,0) |
| 2 | (0,0) | (0,0) | (0,0) |

The combined row-0/row-1 correction C(N_1 mod 3) is respectively
(1,0), (0,0), (1,-1) for residues 0,1,2. Consequently the exact
closed form, for t>=3, is

```text
D(t) = C((A_1(t)+1) mod 3)
       + sum_(b=2..B) F(A_b(t) mod 3, b mod 3).
```

For D=(u,v), the minimum colours are the indices attaining the minimum
of (u,0,-v); and d=max(-2u-v,u-v,u+2v). These formulas include ties.
Each row remainder has colour spread at most one, as does the combined
boundary correction. Thus spread<=B, ||D||_infinity<=B and d<=2B.
These are elementary upper bounds, not evidence of boundedness.

### Exact verification completed

`experiments/colour_imbalance.py` uses integer division and `bit_length`
to find A_b: floor(log_2(t/3^b))=(t//3^b).bit_length()-1. No numerical
logarithm is used for correctness. It computes the closed row counts
and D afresh at every smooth cutoff and compares them with the
independently updated participation births. It also reconstructs the
coordinate and numerical corners and checks the saved optimum witnesses
at all 720 solver cutoffs through 10^14, using the existing comparison
routine. The frozen excess source SHA-256 is checked before use.

Results: **33,742/33,742 smooth cutoffs through 54*4^160 agree**;
**720/720 saved solver/corner comparisons agree**; all **161 saved
nearest-power b coefficients, indices 0..160, agree exactly**. The
completed analysis also directly rechecks **2391/2391 saved frozen-rule
count/d/delta_d rows** in `density-contributions.csv`, through 54*4^40.
At the
last cutoff 54*4^160=2^321*3^3, counts are (11247,11247,11248),
D=(0,-1), d=1. Verification and source hashes are saved in
`experiments/colour-imbalance-verification.json`.

Commands/results for this completed step:

```bash
python3 experiments/colour_imbalance.py
python3 -m py_compile experiments/colour_imbalance.py
git diff --check
```

During development, an inline exploratory command had an unmatched
parenthesis, and the first verification run caught a sign error in the
displayed D-to-d expression at t=6. Both were corrected before the
successful full run; neither indicated a disagreement in the row rule.
Remaining work in this round: rotation regrouping, exact growth and
coefficient partial sums, continued-fraction comparisons, and tests of
minimum-colour interval/Sturmian codings.

Commit workflow: the first ordinary `git add` failed because this
environment mounts the original `.git` directory read-only (could not
create `.git/index.lock`). A writable checkout at
`/tmp/erdos168-round1-checkout` is used for the required commits and
`git push origin work`; changed files are copied there from this shared
workspace. The original checkout's git metadata cannot be advanced here.

### Proved rotation regrouping: the bounded summand has zero mean

With x=log_2(t) and theta=log_2(3), A_b=floor(x-b*theta) exactly.
This makes D a rotation sum with the three-state clock b mod 3. To
obtain one ordinary circle rotation, group rows b=2+3q+j, j=0,1,2.
For B>=2 write B-1=3Q+R, 0<=R<3, and set u=(x-2*theta)/3. Define

```text
G(y)=sum_(j=0..2) F(floor(3*{y-j*theta/3}), (2+j) mod 3).

D(t)=C((A_1+1) mod 3) + sum_(q=0..Q-1) G(u-q*theta)
     + sum_(j=0..R-1)
         F(floor(3*{u-Q*theta-j*theta/3}), (2+j) mod 3).
```

The last sum has at most two terms. This follows from
floor(3y) mod 3=floor(3*{y}). The formula for B=1 is just C.
The means of the three columns of F are (1,1)/3, (1,-2)/3,
(-2,1)/3, so **G has mean zero**. Each coordinate has total variation
6. The discontinuities lie at (j*theta+i)/3 modulo 1, for 0<=i,j<=2;
irrationality of theta makes these nine points distinct.

The standard Denjoy--Koksma inequality therefore bounds each coordinate
of a complete q_n-term G sum by 6 when q_n is a convergent denominator
of theta. Including C and the final two rows gives ||D||_infinity<=9
when Q=q_n. More generally, decomposing Q into its Ostrowski blocks
gives 6 times the sum of its digits, plus 3, as a bound. The external
inequality used here is stated in Proposition 4.2 of
[Fayad--Kanigowski, Multiple mixing for a class of conservative surface flows](https://link.springer.com/article/10.1007/s00222-015-0596-6).
This is a use of a classical theorem on paper, not a Lean proof.

Uniform equidistribution for the fixed, Riemann-integrable step function
G also gives D(t)=o(log t) and d(t)=o(log t). To see why the changing
starting phase u causes no problem, sandwich each step coordinate by
continuous upper and lower functions whose integrals differ by an
arbitrarily small amount; continuous functions have uniform rotation
averages (first prove this for Fourier polynomials using finite
geometric sums, then approximate uniformly). Since Q is proportional
to log t and the boundary terms are bounded, the assertion follows.
Neither this argument nor Denjoy--Koksma proves an O(log log t) or an
O(sqrt(log t)) bound for this particular theta. Bounded partial
quotients of log_2(3) have not been assumed or established.

### Proved unboundedness already along powers of three

At t=3^k, put z=exp(2*pi*i/3) and Z_k=sum_j c_j(3^k)*z^j.
For row b>=1 use n=k-b, so its length is floor(n*theta)+1 and its
normalized colour is a+n. Geometrically summing each row yields

```text
(1-z)*Z_k
  = 1-z^(floor((k-1)*theta)+2)
    + z^(-k) * (sum_(n=0..k-1) z^n
                - z*sum_(n=0..k-1) z^floor(n*(theta+1))),  k>=1.
```

The first term and sum z^n are bounded. Write alpha=(theta+1)/3 and
W_k=sum_(n<k) z^floor(3*{n*alpha}). If D(3^k) were bounded, then Z_k
and W_k would be bounded. If N_j(k) counts the visits {n*alpha} to
[j/3,(j+1)/3), then W_k=sum_j N_j(k)*z^j and
N_0(k)-k/3=(2/3)*Re(W_k). This would give bounded discrepancy for an
interval of length 1/3 under an irrational rotation, which is impossible.
The bounded-remainder interval criterion is |I| in alpha*Z+Z;
1/3 is not in this group because alpha is irrational. This criterion
is stated on page 1 of
[Haynes--Koivusalo, Constructing bounded remainder sets and cut-and-project sets which are bounded distance to lattices](https://arxiv.org/pdf/1402.2125),
with attribution to Hecke, Ostrowski and Kesten; Kesten's original
[1966 paper](https://www.impan.pl/en/publishing-house/journals-and-series/acta-arithmetica/all/12/2/96036/on-a-conjecture-of-erdos-and-szusz-related-to-uniform-distribution-mod-1)
is Acta Arithmetica 12, 193--212.

For completeness, the necessary direction needed here has a short
standalone argument. Let f=1_[0,1/3)-1/3 and T(y)=y+alpha. Bounded
partial sums at 0 imply uniformly bounded partial sums at every orbit
point by subtracting two sums at 0. Density of the orbit and right
continuity of every finite step sum extend this bound to every phase.
The functions H_N=(1/N)*sum_(n=1..N) S_n f have bounded L^2 norm and
satisfy H_N-H_N composed with T = f + O(1/N) uniformly. A weak L^2
subsequence gives a real measurable H with H-H composed with T=f.
Then phi=exp(2*pi*i*H) is a nonzero L^2 eigenfunction satisfying
phi composed with T=exp(2*pi*i/3)*phi. A nonzero Fourier coefficient
of phi forces m*alpha=1/3 modulo 1 for an integer m, contradicting
irrationality. Finally theta is irrational, since rational theta=p/q
would imply 2^p=3^q, contradicting unique prime factorization.

Thus **D(3^k) and d(3^k) are unbounded**, unconditionally for the
participating-colour definition. Here d>=max(c_j)-min(c_j)>=||D||_infinity.
This means unbounded record envelopes, not that d(t) tends to infinity;
there are long small-discrepancy stretches and returns. Only the use
of these quantities to describe exact g and its density is conditional
on the frozen rule.

### Exact growth measurements through the requested limit

`experiments/colour_rotation.py` scans all 33,742 smooth cutoffs,
records counts, D, d and delta_d, and computes all b blocks reached by
54*4^160. Norm |D| here means ||D||_infinity; the Euclidean maximum
is also recorded via its exact square. The results are:

| Through 54*4^K | Smooth cutoffs | max ||D||_infinity | max d |
| --- | --- | --- | --- |
| K=0 | 16 | 2 | 3 |
| K=5 | 92 | 2 | 4 |
| K=10 | 231 | 2 | 4 |
| K=20 | 698 | 2 | 4 |
| K=40 | 2391 | 3 | 5 |
| K=80 | 8803 | 3 | 5 |
| K=120 | 19254 | 3 | 6 |
| K=160 | 33742 | 4 | 6 |

The maximum |c_0-c_1| is 4, maximum |c_1-c_2| is 3, maximum colour
spread is 4, and maximum Euclidean |D| is sqrt(20). The coordinate
and spread maximum 4 occurs **only twice**: t=2^199*3^73 and
t=2^199*3^76. At the first, counts=(10502,10498,10500), D=(4,-2).
The maximum d=6 occurs at 17 cutoffs, first at t=2^95*3^73,
counts=(4727,4727,4724), D=(0,3), and last at t=2^209*3^73.
The first larger records are:

| t factorization | x=log_2 t (display) | D | d | Newly reached record |
| --- | --- | --- | --- | --- |
| 2^1*3^1 | 2.5849625 | (1,-1) | 2 | norm 1, d 2 |
| 2^4*3^1 | 5.5849625 | (2,-1) | 3 | norm 2, d 3 |
| 2^3*3^8 | 15.6797000 | (0,2) | 4 | d 4 |
| 2^50*3^8 | 62.6797000 | (3,-1) | 4 | norm 3 |
| 2^31*3^20 | 62.6992500 | (3,-2) | 5 | d 5 |
| 2^95*3^73 | 210.7022626 | (0,3) | 6 | d 6 |
| 2^199*3^73 | 314.7022626 | (4,-2) | 6 | norm 4 |

Seven-point exploratory least-squares fits to the max-d envelope,
using K=5,10,20,40,80,120,160 and x=2K+log_2(54), give R^2=0.90366
for an affine function of x, 0.92461 for an affine function of sqrt(x),
and 0.87867 for an affine function of log(x). These small, dependent,
staircase samples **do not identify an asymptotic growth law**. The
proved sublinear bound above excludes asymptotically positive linear
growth in log t, despite the finite-range fit.

### Exact b coefficients and both meanings of partial sum

The limit lies between 3^205 and 3^206, so it covers complete blocks
k=0..204 and part of block 205. The last coefficient is explicitly
marked truncated in the data. All coefficients and sums use Fraction.

| Last index | Unweighted sum b_k (display) | Weighted sum b_k/3^k (display) |
| --- | --- | --- |
| 20 | 0.477596821729 | 0.208427869725 |
| 40 | -10.543271062718 | 0.208427869765 |
| 80 | -17.802145728008 | 0.208427869765 |
| 120 | -30.141470698083 | 0.208427869765 |
| 160 | -64.635767251671 | 0.208427869765 |
| 204, complete | -70.870603276188 | 0.208427869765 |
| 205, truncated at 54*4^160 | -71.567938707823 | 0.208427869765 |

The largest individual |b_k| remains
718505744573433/281474976710656=2.552645187042774..., at k=32,
where b_k is negative. The largest unweighted partial sum is
2.2139895083528245 at k=24; the smallest is -72.86918028640869 at
k=203. The affine fit to all complete partial sums k=1..204 is
10.11599309-0.40739753*k, R^2=0.93924; square-root and logarithmic
fits have R^2=0.85188 and 0.63743. This is empirical negative drift,
not a proof that the unweighted partial sums diverge or that individual
b_k are unbounded. Weighted absolute convergence was already proved
from |delta_d|<=2 and the smooth reciprocal sum.

Summation by parts makes the distinction explicit:

```text
b_k = d(3^(k+1)-)/3 - d(3^k-)
      + 3^k * integral_(3^k..3^(k+1)) d(t)/t^2 dt.
```

Hence a bound d<=M on a block, including its left limit, implies
|b_k|<=M. Unbounded d alone does not imply unbounded b_k; a constant
part of d cancels in this formula. **Uniform boundedness of the b_k
and boundedness/divergence of their unweighted partial sums remain open.**

### Continued-fraction records and a longer exact powers-of-three audit

The script certifies the continued-fraction prefix
[1;1,1,2,2,3,1,5,2,23] using the exact bracket
50508/31867 < theta < 24727/15601. Each endpoint comparison is
checked by comparing 3^q with 2^p; Decimal only proposes the bracket
and displays errors. The relevant convergents and signed errors are:

| p/q | q*theta-p (display) |
| --- | --- |
| 3/2 | +0.1699250014 |
| 8/5 | -0.0751874964 |
| 19/12 | +0.0195500087 |
| 65/41 | -0.0165374704 |
| 84/53 | +0.0030125382 |
| 485/306 | -0.0014747793 |
| 1054/665 | +0.0000629796 |
| 24727/15601 | -0.0000262492 |

The two first records near x=62.7 have ratio 3^12/2^19; their phase
separation is exactly 12*theta-19. Their grouped row length Q is 12,
exactly the corresponding denominator. The first d=6 record changes
the incoming row exponent from b=20 to b=73=20+53; its fractional-x
phase moves by 53*theta-84. This is a concrete near-return relation.
The grouped lengths at the later d=6 and norm-4 records are 43 and
65; they are not themselves denominators 41 and 53. The data support
continued-fraction resonance, **not a rule that every record occurs
exactly at a convergent denominator**. The full requested scan only
reaches Q=68, so denominators 306 and 665 require a longer audit.

At t=3^k, a linear-time exact recurrence maintains the normalized
sum of Q(floor(n*theta)+1,-n) for 0<=n<k, cyclically relabels colours
by -k, and adds Q(floor((k-1)*theta)+2,0) for row 0. Floors come from
the bit length of 3^n. The program verifies its complex rotation-word
identity in Z[z]/(1+z+z^2) at **all 8192 indices**, matches the direct
row formula at all k<=205, and also at k=306,665,918,1995,8192.

| Powers-of-three audit through k | max ||D(3^k)||_infinity | max d(3^k) |
| --- | --- | --- |
| 205 | 1 | 2 |
| 306 | 1 | 2 |
| 665 | 2 | 4 |
| 1024 | 2 | 4 |
| 1995 | 3 | 6 |
| 4096 | 5 | 9 |
| 8192 | 9 | 15 |

Exploratory fits on these seven longer-audit checkpoints have R^2=0.98589
for an affine function of k (equivalently log t), 0.98187 for sqrt(k),
and 0.87172 for log(k). The resonance over this finite range makes
linear and square-root fits both plausible numerically; the proved
sublinear bound still forbids a positive asymptotic linear slope.

Both final maxima first occur at **k=7747**, with D=(6,-9). Record
families include k=1762,3757,5752,7747, spaced by 1995=3*665;
their D vectors are (3,-3),(4,-5),(5,-7),(6,-9). Another family has
k=2427,4422,6417, also spaced by 1995. Since 1054+665 is divisible
by 3, the rotation alpha has the near-return 573/665, with
665*alpha-573=(665*theta-1054)/3. The large next partial quotient
23 explains the extended repeating resonance before the next theta
denominator 15601. This explanation of the observed records is
consistent with the exact identities; it is not an asymptotic fit.
At k=41,53,306,665 the counts actually tie, so the denominators are
near-return controls rather than locations of maximal discrepancy.

### Minimum-colour coding: precise counterexamples and limitations

Let M(t) be the full set of minimum colours. The script also tests
the least index in M(t), so ties cannot be hidden by arbitrary choices.
For all smooth t, {x} alone cannot determine M: the first repeated
phase conflict at t>=3 is t=3 versus 6. More strongly, the first
conflict with **two different unique minima** is t=6 versus 12:
both have 2^{ {x} }=3/2, but counts are (2,1,2) and (3,3,2), so
M={1} and {2}. This rejects every coding solely by {x} over the
full domain, not just a particular interval catalog.

For two-phase tests, use exact coordinates
R2=t/2^floor(x) in [1,2), R3=t/3^floor(x/theta) in [1,3).
Rectangles formed from R2 thresholds 1,9/8,3/2,27/16,2 and R3
thresholds 1,9/8,3/2,27/16,2,3 first conflict at t=6 versus 24,
with unique minima 1 and 0. Both lie in the same box
R2 in [3/2,27/16), R3 in [2,3). A second tested pair, {x/3} and
{x/theta}, uses t/8^floor(x/3) thresholds 1,2,4,8 and the same R3
thresholds; its first conflict is t=18 versus 24, M={0,1,2} versus
{0}. These reject the **specified boxes**, not arbitrary partitions
of an unspecified torus phase.

At 3^k, all three natural thirds catalogs fail at k=8:

- For {k*theta}, k=3 and 8 are both in [2/3,1), with M={0,1,2}
  and {2}. Membership is checked exactly by cubing
  3^k/2^floor(k*theta) and comparing with 2 and 4.
- For {k*theta/3}, k=2 and 8 share [0,1/3), with the same conflict.
- For {k*(theta+1)/3}, k=1 and 8 share [2/3,1), again with that conflict.

Even allowing arbitrary interval edges, the necessary number of
constant intervals on the line [0,1), ordered by phase, grows as follows.
These are exact adjacent-label transition counts, without fitted
rounding errors:

| k=1..K | M on {k*theta} | least M on {k*theta} | M on {k*theta/3} | M on {k*(theta+1)/3} |
| --- | --- | --- | --- | --- |
| 40 | 32 | 28 | 26 | 29 |
| 160 | 43 | 39 | 26 | 127 |
| 205 | 43 | 39 | 26 | 127 |
| 665 | 563 | 515 | 292 | 564 |
| 1995 | 1851 | 1622 | 1865 | 1750 |
| 4096 | 3958 | 3793 | 2946 | 3908 |
| 8192 | 8062 | 7902 | 3011 | 8039 |

A circle partition can save at most one interval by joining the first
and last runs. Cyclically normalizing M by adding k is also tested;
even that needs 1238 intervals on {k*theta} through 8192. The report
contains all normalized-label and least-index counts.

For a reproducible fitted-catalog holdout, train on k=1..40, take
each maximal constant-label run in phase order, and place its boundary
at the exact midpoint between adjacent unequal-label **ratio** values.
The {k*theta} fit (32 intervals) first fails at k=44, predicting all
three minima instead of {2}. The {k*theta/3} and alpha-phase fits
first fail at k=41. These are first counterexamples to these explicit
fitted catalogs, not universal counterexamples to all possible edges.

Binary indicators of membership in M fail Sturmian balance. For colour
0 the length-2 blocks starting at k=1 and 8 are 11 and 00, first
exposing imbalance at k=9. For colour 1, length-4 blocks starting at
1 and 8 are 1111 and 0110 (first at k=11). For colour 2, starts 1
and 13 give 1111 and 0110 (first at k=16). The least-minimum binary
indicators fail as well, and each membership indicator has a 00/11
conflict even when the sample starts at k=1024. Thus these observed
binary words are not Sturmian. Failure after finitely many starts
does not prove that every tail fails balance.

**Plain conclusion:** the row-count hypothesis is proved, and the
imbalance is exactly a finite-step-function rotation **sum**, with
unbounded discrepancy state. Three-distance/continued-fraction
methods apply to its visit counts and near returns. The minimum is
the nonlinear minimum of the accumulated counts, not a demonstrated
local rotation label. The tested simple catalogs and Sturmian
interpretations fail. An **eventual fixed finite-interval coding of
M(3^k) has neither been proved nor disproved**. Because {k*theta} is
injective for finite k, any finite sample can be fitted with enough
intervals; a finite list of labels cannot by itself refute the existence
of some unspecified finite partition. The same limitation applies to
unspecified extra torus phases. No claim of universal impossibility
or eventual stabilization is justified by these tests.

### Round 1 artifacts, validation, and remaining issues

New artifacts under `experiments/`:

- `colour_imbalance.py`, `colour-imbalance-verification.json`: exact row
  formula, independent birth/corner/solver comparisons and source hashes.
- `colour_rotation.py`, `colour-rotation.json`: growth records,
  Fraction partial sums, certified continued fractions, specified coding
  counterexamples, exact interval-complexity counts, and exploratory fits.
- `colour-imbalance-cutoffs.csv`: all 33,742 smooth cutoffs through
  54*4^160, counts, D, spread, d, delta_d and the minimum-set bitmask.
- `colour-imbalance-coefficients.csv`: all 206 reached blocks,
  rational b_k and weighted/unweighted partial sums; block 205 is truncated.
- `colour-imbalance-powers3.csv`: all k=0..8192, counts, D, d, both
  minimum labels and floor(k*theta). The bitmask uses bit j for colour j.

Commands for the completed analysis:

```bash
python3 experiments/colour_imbalance.py
python3 experiments/colour_rotation.py
python3 -m py_compile experiments/colour_imbalance.py experiments/colour_rotation.py
git diff --check
git diff --cached --check
```

The extended powers audit is linear in the number of powers and does
not run a solver. Phase orders, memberships, counts, coefficients and
counterexamples are exact. Regressions use floating point for display
and are explicitly exploratory. The computation completed in minutes,
well below the 60-minute limit; no computation was abandoned at that
limit. No Lean, theorem statement, wallet, key or secret was changed.

Remaining mathematical issues: prove the frozen g rule beyond the
solver range; analyze b_k boundedness and unweighted partial-sum drift;
settle any precisely formulated eventual minimum-colour coding; derive
a useful uniform continued-fraction/Ostrowski description that retains
the accumulated discrepancy. The next step should use the proved
three-interval rotation discrepancy and its boundary correction as the
state for the frozen minimum/excess condition, rather than assuming
that a few phase thresholds alone determine the minimum or b_k.
