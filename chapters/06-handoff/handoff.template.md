<!--
handoff.template.md. Chapter 6, Appendix A3. The file that carries a decision
to any executor. Governed by one rule: *not in this file, it didn't happen.*

The contract runs both ways: instructions down, results and rulings back, every
section with a clear owner. Contract on the GATE, not the code. Any
implementation that clears the verification gate is acceptable.

Lint it before you hand it over (catches a missing section or a thresholdless gate):
    node contract-lint.js ../../worked-examples/handoff.md

This is the full clean template (Appendix A3). A filled 7-section instance ships
at ../../worked-examples/handoff.md.
-->

# Handoff: <task>

## TL;DR
<one or two sentences: what and why>

## Context (read-only — do NOT change these)
<the facts the executor needs: paths, secrets by name, protocols>

## Task
<the specific typing steps, from the plan>

## Constraints (frozen — violating any of these fails the handoff)
<falsifiable boundaries: which files only, what never to log, which library>

## Verification gate (run these, paste RAW output into Raw Results)
| Gate | Command | Threshold | Verdict |
|------|---------|-----------|---------|
| ...  | ...     | ...       |         |

## Escalation triggers (STOP and hand back if:)
<the conditions under which the executor must not guess>

## Open disagreements (builder logs; architect rules)
| Builder's view | Spec says | Evidence | Architect ruling |
|----------------|-----------|----------|------------------|

## Raw results (builder writes; architect never edits)

## Decisions log (architect only)
