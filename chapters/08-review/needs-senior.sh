#!/usr/bin/env bash
# needs-senior.sh -- Chapter 8. Route the review by the paths the diff touches.
# High-stakes paths earn a Fable review pass; a rename or copy tweak ships on its gate.
#
# The book generates the changed-files list from git:
#     git diff --name-only main > changed.txt
#     bash needs-senior.sh changed.txt
# Offline, it reads any such list from an argument file:
#     bash needs-senior.sh ../../worked-examples/changed.txt
# Runs offline, zero keys. Only grep + POSIX shell.
set -u
changed="${1:-changed.txt}"

# A missing list must NOT read as an all-clear. Without this guard, grep fails on a
# nonexistent file, the else branch fires, and the script prints "SHIP ON GATE" with
# exit 0 -- a false pass on the very gate you were counting on.
if [ ! -f "$changed" ]; then
  echo "needs-senior.sh: no changed-files list at '$changed'." >&2
  echo "  generate one:  git diff --name-only main > changed.txt" >&2
  echo "  or pass a path: bash needs-senior.sh ../../worked-examples/changed.txt" >&2
  exit 2
fi

if grep -qiE '(webhook|payment|billing|auth|token|secret|crypto|session)' "$changed"; then
  echo "FABLE REVIEW -- high-stakes paths in this diff:"
  grep -iE '(webhook|payment|billing|auth|token|secret|crypto|session)' "$changed"
else
  echo "SHIP ON GATE -- no high-stakes paths; skip the senior pass"
fi
