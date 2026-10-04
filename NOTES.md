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
- Timed challenge compilation remains unverified. `lake env lean tasks/erdos-168-ii/Challenge.lean` stops at the first import because the blocked cache prevented building its dependencies; its 0.717-second failed run is **not** a successful compilation time.
- On a machine with access to the Mathlib cache host, run the commands in `README.md` and record the successful compile time here.
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
