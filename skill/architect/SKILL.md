---
name: architect
description: Classify a task as judgment or typing, route it to the cheapest
  correct seat, and emit a handoff. Use at the start of any non-trivial task.
---

# /architect — route this task before doing it

When invoked with a task, do NOT start doing it. Route it first.

## Step 1 — Classify

- **JUDGMENT**: deciding what's wrong / what to build / what order / whether work is
  correct or safe. Verbs: decide, diagnose, design, evaluate, review, plan.
- **TYPING**: producing the output of a decision already made. Verbs: implement,
  write, rename, generate, apply, execute-this-step.
- **MIXED**: both (most real tasks). The parts get DIFFERENT seats.

If you cannot cleanly classify it, route the deciding part to Fable and let the
decision reveal the typing. (Uncertainty means a decision hasn't been made yet.)

## Step 2 — Assign a seat

- JUDGMENT → Fable (`--model fable`), effort high or xhigh. Never types.
- TYPING, specified logic → Sonnet (`--model sonnet`), effort medium.
- TYPING, mechanical, no fresh knowledge, fits 200K → Haiku (`--model haiku`).
- MIXED → do the judgment on Fable now, then emit a handoff for the typing.

## Step 3 — For JUDGMENT/MIXED, do the judgment, then emit a handoff

Write `docs/handoff-<slug>.md` with: Context (read-only), Task (the typing steps),
Constraints (frozen, including files-touched), a Verification gate (commands +
thresholds), Escalation triggers, and a per-step Owner model. Do the judgment
part yourself on Fable; write the typing part into the handoff for a cheaper seat.

## Step 4 — Report the route, don't run the typing

Output: the classification, the assigned seat(s), the exact command to execute the
typing (e.g. `claude --model sonnet "$(cat docs/handoff-x.md)"`), and the handoff
path. Do NOT execute the typing yourself on the expensive seat.
