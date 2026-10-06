#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checkout="$root/vendor/formal-conjectures"
patch="$root/vendor/formal-conjectures-audit-fixes.patch"
repository="https://github.com/google-deepmind/formal-conjectures.git"
base="7d1a8c9912747679d0093f6d1216420c33ee5ffa"
expected="6a786f997e18e8f095762a2830d191b7e25e505e"
patch_hash="82b0f491dd18c331f12efa722761e46b728e9bb8d643466e9ef8b40dde903023"

actual_hash="$(sha256sum "$patch" | cut -d ' ' -f 1)"
if [[ "$actual_hash" != "$patch_hash" ]]; then
  echo "Formal Conjectures patch hash mismatch" >&2
  exit 1
fi

if [[ ! -d "$checkout/.git" ]]; then
  if [[ -e "$checkout" ]]; then
    echo "Existing non-Git directory: $checkout" >&2
    exit 1
  fi
  git clone --filter=blob:none --no-checkout "$repository" "$checkout"
  fresh=1
fi

# A --no-checkout clone has an empty work tree, which Git reports as deletions.
if [[ -z "${fresh:-}" && -n "$(git -C "$checkout" status --porcelain)" ]]; then
  echo "Formal Conjectures checkout has local changes: $checkout" >&2
  exit 1
fi

if [[ "$(git -C "$checkout" rev-parse HEAD)" == "$expected" ]]; then
  exit 0
fi

git -C "$checkout" fetch --no-tags origin "$base"
git -C "$checkout" checkout --detach "$base"
git -C "$checkout" apply "$patch"
git -C "$checkout" add --all
source_tree="$(git -C "$checkout" write-tree)"
derived="$(
  printf '%s\n' 'fix(ErdosProblems): correct audited candidate statements' |
    GIT_AUTHOR_NAME='Conjectures Pool Builder' \
    GIT_AUTHOR_EMAIL='pool@conjectures.io' \
    GIT_AUTHOR_DATE='2026-08-03T00:00:00Z' \
    GIT_COMMITTER_NAME='Conjectures Pool Builder' \
    GIT_COMMITTER_EMAIL='pool@conjectures.io' \
    GIT_COMMITTER_DATE='2026-08-03T00:00:00Z' \
    git -C "$checkout" commit-tree "$source_tree" -p "$base"
)"
if [[ "$derived" != "$expected" ]]; then
  echo "Formal Conjectures derived commit mismatch: $derived" >&2
  exit 1
fi
git -C "$checkout" checkout --detach "$derived"
test -z "$(git -C "$checkout" status --porcelain)"

