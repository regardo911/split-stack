#!/usr/bin/env bash
# plan-check.sh -- Chapter 5. The plan greps, as one script.
#
# Five fields per step, no exceptions. So the total field count should be a clean
# multiple of five with every label at equal count -- a label that comes up short
# is the field a step dropped, which is the field a cheap seat will be forced to
# guess. Then it flags Change lines vague enough to hide a decision.
#
# Usage: bash plan-check.sh plan.md
# Exits 1 if a field is missing or a Change line trails off. Offline, grep only.
set -u

plan="${1:-plan.md}"
[ -f "$plan" ] || { echo "plan-check: no such file: $plan" >&2; exit 2; }

fields='^- (Goal|Files touched|Change|Owner model|Done when):'
vague='appropriately|as needed|relevant|proper(ly)?|and so on|etc\.'
fail=0

total=$(grep -cE "$fields" "$plan" || true)
echo "field lines: $total"
grep -oE "$fields" "$plan" | sort | uniq -c

if [ "$total" -eq 0 ]; then
  echo "FAIL: no '- Goal:/- Files touched:/- Change:/- Owner model:/- Done when:' lines at all."
  fail=1
elif [ $((total % 5)) -ne 0 ]; then
  echo "FAIL: $total is not a clean multiple of 5 -- a step dropped a field."
  fail=1
else
  # every label at equal count? count the distinct per-label tallies.
  spread=$(grep -oE "$fields" "$plan" | sort | uniq -c | awk '{print $1}' | sort -u | wc -l | tr -d ' ')
  labels=$(grep -oE "$fields" "$plan" | sort -u | wc -l | tr -d ' ')
  if [ "$labels" -ne 5 ] || [ "$spread" -ne 1 ]; then
    echo "FAIL: the five labels are not at equal count -- a step dropped a field."
    fail=1
  else
    echo "OK: $((total / 5)) steps, five fields each, every label at equal count."
  fi
fi

echo
echo "vague Change lines (each hides a judgment the cheap seat will guess at):"
if grep -nEi "$vague" "$plan"; then
  echo "FAIL: rewrite each hit into something a cheap seat can type without deciding."
  fail=1
else
  echo "  none -- every line is concrete."
fi

echo
echo "This is a spot-check, not a proof: a decision can still hide in specific-looking"
echo "prose the grep will not flag. The real test is handing one step to a cheap seat."
exit "$fail"
