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
