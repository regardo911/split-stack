#!/usr/bin/env bash
# The shell + node checkers, on inputs the reader supplies.
#
#     bash tests/test_checkers.sh
#
# Offline, zero keys. Needs bash and node.
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass=0
fail=0

check() { # check <name> <expected-substring> <actual-output>
  if printf '%s' "$3" | grep -qF -- "$2"; then
    echo "  ok   $1"
    pass=$((pass + 1))
  else
    echo "  FAIL $1 -- expected to find: $2"
    printf '%s\n' "$3" | sed 's/^/       | /'
    fail=$((fail + 1))
  fi
}

echo "gate.sh -- any Blocker or Major sends it back; else ship"
out=$(bash "$ROOT/chapters/08-review/gate.sh" "$ROOT/worked-examples/verdict.md")
check "a BLOCKER sends it back"        "DECISION: SEND BACK" "$out"
check "and it tallies the findings"    "blocker=1 major=0"   "$out"

out=$(bash "$ROOT/chapters/08-review/gate.sh" "$ROOT/worked-examples/verdict-clean.md")
check "minors and nits still ship"     "DECISION: SHIP"      "$out"

# a MAJOR alone, with no blocker, must also send back
printf -- '- MAJOR    src/billing/totals.ts:118 — rounds before the split\n' > "$TMP/major.md"
out=$(bash "$ROOT/chapters/08-review/gate.sh" "$TMP/major.md")
check "a lone MAJOR sends it back"     "DECISION: SEND BACK" "$out"

echo
echo "needs-senior.sh -- route the review by the paths the diff touches"
out=$(bash "$ROOT/chapters/08-review/needs-senior.sh" "$ROOT/worked-examples/changed.txt")
check "flags the high-stakes paths"    "FABLE REVIEW"            "$out"
check "and names the file that earned it" "src/webhooks/payments.ts" "$out"

printf 'README.md\nsrc/ui/button.tsx\n' > "$TMP/benign.txt"
out=$(bash "$ROOT/chapters/08-review/needs-senior.sh" "$TMP/benign.txt")
check "a benign diff ships on its gate" "SHIP ON GATE"           "$out"

echo
echo "contract-lint.js -- does the handoff close the four gaps?"
out=$(node "$ROOT/chapters/06-handoff/contract-lint.js" "$ROOT/worked-examples/handoff.md")
check "a complete contract passes"     "all 5 structural checks pass" "$out"

# strip the Escalation section: the executor loses its stop-and-hand-back valve
sed '/^## Escalation/,/^## Raw results/d' "$ROOT/worked-examples/handoff.md" > "$TMP/no-escalation.md"
out=$(node "$ROOT/chapters/06-handoff/contract-lint.js" "$TMP/no-escalation.md")
check "a missing Escalation section is a GAP" "GAP Escalation" "$out"
check "and the verdict counts it"             "1 gap(s)"       "$out"

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
