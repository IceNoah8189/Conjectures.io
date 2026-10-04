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
