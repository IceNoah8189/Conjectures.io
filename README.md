# Erdős 168 part ii

This repo contains the unchanged Conjectures.io challenge in `tasks/erdos-168-ii/` and a Lean v4.33.1 project using the validator's pinned Mathlib version.

## Set up on another machine

Install [elan](https://github.com/leanprover/elan), then run from the repo root:

```sh
bash scripts/setup-deps.sh
lake exe cache get
lake build TaskSupport
lake env lean tasks/erdos-168-ii/Challenge.lean
```

The Formal Conjectures dependency is reconstructed from the audited source patch. The Mathlib step downloads prebuilt artifacts. The challenge intentionally still has `sorry`; a successful compile confirms the setup, not the theorem.

See `NOTES.md` for source commits and local verification results.
