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
