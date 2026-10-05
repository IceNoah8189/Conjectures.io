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
