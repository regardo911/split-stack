<!--
delegation-brief.template.md. Chapter 7, Appendix A5. Scopes an executor run
so it can't run away. It's the handoff contract plus an explicit budget on HOW
the work may be done. Two files: this spec, and a state.template.md the executor
updates as it goes.

Run one supervised pass on the cheap seat:
    claude --model sonnet --effort medium "$(cat delegation-brief.md)"
Read the run's cost from `claude -p --output-format json` or the session trace.

The three runaways this closes: fan-out (75 Fable sub-agents ≈ $49 in 10 min),
reading too much, and over-engineering. All three are the executor making
decisions you meant to keep. The hard-limits block closes that room.
-->

# Delegation brief: <task>
- Plan steps to run: <which plan.md steps, in order>
- Files-touched boundary: <the only files that may change; nothing else>
- Concurrency: serial, no sub-agents (raise deliberately, only for disjoint work)
- Effort cap: medium (typing doesn't need high)
- Model: sonnet for typing; escalate to fable only on a tagged judgment step
- Verification gate: <the commands to run, and the thresholds that must pass>
- Escalation triggers: <the conditions that STOP the run and hand back to you>
- Log: every escalation, with its step and its reason
- State file: state.md, updated after every step
- Stop condition: one supervised pass, then read the cost

## Sub-agent budget (hard rules, if you fan out at all)
- Never more than 4 sub-agents at once. Prefer serial.
- Only fan out for genuinely independent work with disjoint files.
- Every sub-agent runs --model sonnet unless a step is tagged for judgment.
- One Fable escalation at a time, logged, only on a tagged step.

<!--
If you later wire in the API advisor tool (Chapter 10), its consult tokens sit
OUTSIDE the request-level max_tokens and any task_budget. Cap it on the tool
definition itself. An advisor without these fields is the one uncapped seat:
  {"type": "advisor_20260301", "name": "advisor", "model": "claude-fable-5",
   "max_uses": 3, "max_tokens": 2048}

The three scoping controls, three behaviors:
  - max_tokens        : one response's length, hard ceiling, model unaware
  - task_budget (beta): a run's token spend, soft (model self-moderates), min 20,000
  - --max-budget-usd  : dollars on a `claude -p` headless run, hard kill-switch
-->
