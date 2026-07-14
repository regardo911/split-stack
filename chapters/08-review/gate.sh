#!/usr/bin/env bash
# gate.sh -- Chapter 8. Collapse a graded verdict into one ship / send-back call.
# The rule made mechanical: any Blocker or Major sends it back; else ship.
#
# Usage: bash gate.sh ../../worked-examples/verdict.md
# Runs offline, zero keys. Only grep + POSIX shell.
set -u
verdict="${1:-verdict.md}"

count() { grep -cE "^[-*][[:space:]]+$1\\b" "$verdict" || true; }
blk=$(count BLOCKER); maj=$(count MAJOR)
min=$(count MINOR);   nit=$(count NIT)

printf 'blocker=%d major=%d minor=%d nit=%d\n' "$blk" "$maj" "$min" "$nit"
if [ "$blk" -gt 0 ] || [ "$maj" -gt 0 ]; then
  echo "DECISION: SEND BACK"
  grep -E "^[-*][[:space:]]+(BLOCKER|MAJOR)\\b" "$verdict" || true
else
  echo "DECISION: SHIP (note the minors and nits, then move on)"
fi
