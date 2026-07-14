# 09 · Catch the silent fallback

*"Every one of my questions are getting flagged down to 4.8, just doing software security research."*

Not attacking anything. Researching. And the model bounced the work to Opus 4.8 without a word.

That's the wall, and here is the part that costs you: on the raw API a refusal just stops, but in Claude Code the Opus fallback ships **on by default**. Your work gets rerouted, the session carries on as if nothing happened, and you keep paying. Worse than the money: you may have decided something on Opus-grade judgment while believing it was Fable-grade.

An invisible switch is one you can never price. So make it visible.

```bash
claude -p --model fable --output-format json "your task" > run.json
python3 fallback.py run.json --expect claude-fable-5
```

```
WARNING: served by claude-opus-4-8, not Fable — Opus judgment at Opus rates
```

It reads both shapes. The Claude Code result envelope carries no top-level `.model`, so the served seat comes out of `.modelUsage` (the highest-cost entry did the real work). A raw API response carries `usage.iterations[]`, where a `fallback_message` entry is the fingerprint.

A refusal comes back as structured data, never a dead end: a `category` (one of `cyber`, `bio`, `frontier_llm`, `reasoning_extraction`, `null`), a route, and the `recommended_model` to retry against. Branch on `stop_reason`. Never parse `stop_details.explanation`, which is display text, not a contract.

Try it against the shapes in [worked-examples/refusals/](../../worked-examples/refusals/).

## The thing nobody instruments

A refusal is an **HTTP 200**. It is invisible to every error dashboard you own, because those watch for 5xx. You can be bounced to Opus on a quarter of your requests and stare at a perfectly green board while it happens.

So count it yourself, then decide on purpose: **reroute** (pick the seat, don't let the classifier pick it), **rephrase** (the flag was a false positive on benign work), or **accept** (sometimes the wall is right). Deliberate Opus beats accidental Opus every time. And never iterate on a model you didn't choose: a detected switch invalidates the run's assumptions, not just its bill.
