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
- In this cloud workspace, `lake env lean tasks/erdos-168-ii/Challenge.lean` stopped at the first import because the blocked cache prevented building its dependencies; its 0.717-second failed run was not a compilation time. The challenge was later compiled successfully on the user's PC (below).
- Fixed `scripts/setup-deps.sh` on fresh machines: its `--no-checkout` clone left an empty work tree, which the local-changes check misread as deletions, so setup always stopped there. The check now skips a checkout the script just cloned. Verified that a fresh run reaches `6a786f997e18e8f095762a2830d191b7e25e505e` and that a rerun exits cleanly. To recover a checkout broken by the old script, delete `vendor/formal-conjectures` and rerun.
- On the user's WSL Ubuntu PC, the fixed setup script reached the audited commit, `lake exe cache get` downloaded all 8690 Mathlib files, and `lake build FormalConjectures TaskSupport` then completed (`Build completed successfully (10102 jobs)`).
- **Verified challenge compile (user's WSL Ubuntu PC):** `time lake env lean tasks/erdos-168-ii/Challenge.lean` succeeded in `real 0m7.300s` (`user 0m3.022s`, `sys 0m3.577s`). The only output was the expected `declaration uses \`sorry\`` warning at 6:8 and two `linter.style.moduleDocstring` warnings (lines 4 and 9). The docstring warnings come from the unchanged challenge file and do not block validation.

## Remaining

- Write the proof of the theorem in `tasks/erdos-168-ii/Challenge.lean` without changing its statement. The final file must avoid `sorry`, `admit`, `axiom`, `import`, `set_option`, `native_decide`, `instance`, `macro`, `syntax` and `notation`.
