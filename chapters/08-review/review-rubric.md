<!--
review-rubric.md. Chapter 8. The senior-review prompt that turns a cheap
executor's diff into a graded verdict.md, then a ship / send-back call. ONE pass,
no loops: Fable reviews once, you read the verdict, you decide.

Run it against the diff:
    git diff main > change.diff
    claude --model fable --effort high "$(cat review-rubric.md)
    $(cat change.diff)"

Then collapse the verdict to a decision with the shell gate:
    bash gate.sh verdict.md
A worked verdict ships at ../../worked-examples/verdict.md (1 blocker → SEND BACK) and
../../worked-examples/verdict-clean.md (no blocker/major → SHIP).

Route the review the same way you route the work. High-stakes paths only:
    bash needs-senior.sh ../../worked-examples/changed.txt
-->

Fresh context: you did not write this diff and you do not defend it.
Try to prove it does NOT meet the spec; a pass you can't break is the only pass.

Review this diff as a senior engineer. Do NOT edit anything; produce a verdict
only. Grade every finding:
  BLOCKER (ships broken / security / data loss / breaks done-criteria)
  MAJOR   (real bug under a plausible input, tests missed it)
  MINOR   (missing edge case / weak error handling)
  NIT     (style / naming, no behavior impact)
For each: severity, file:line, one-sentence why, the concrete fix.

Check the diff against the handoff's constraints and gate. Did the executor
edit only the allowed files and honor every frozen constraint? And check the
GOAL, not just the code: does this diff accomplish the plan's actual goal, or
just pass its gate? Clean code that solves the wrong problem is a finding.

End with VERDICT: SHIP or SEND BACK (list exactly what must change).

<!--
The gate the verdict collapses to: any Blocker or Major → SEND BACK, else SHIP.
Nits and Minors never block. The verdict is an input to your decision, not the
decision itself. Go to the file:line and confirm a Blocker is real before you
route a fix. A review that's always right is a review you've stopped reading.
-->
