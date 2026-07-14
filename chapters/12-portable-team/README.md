# 12 · The team that survives the next model

There was a stretch where you simply could not get Fable 5. Not rate-limited. Not expensive. Gone.

The developers who had fused their whole setup to "Fable does everything" were dead in the water. Their prompts said Fable. Their scripts hardcoded it. Their choice was to wait, or to rebuild on a different model and re-tune every prompt they'd tuned for Fable's specific behaviour.

The ones who had built a *stack* changed one thing: which model sat in the architect seat. The audit prompt, the plan template, the handoff contract, the router. None of them cared who filled the seat, so nothing else had to move.

You don't have to take that on faith. Prove it, the way you've proved everything else here.

## The swap drill

```bash
claude --version                                       # do the aliases still resolve?
claude --model best                                    # Fable where entitled, else the latest Opus
export ANTHROPIC_DEFAULT_FABLE_MODEL="<a-profile-your-org-allows>"
```

Then run the router on a real task:

```
/architect audit the payments module for security issues
```

Same classification. Same seat assignment. Same handoff. A different model doing the judging. You just hot-swapped the most expensive component in the stack and the machine didn't notice, because **not one artifact here hardcodes a model name.** They name seats.

| Artifact | The seat it names | Model today |
|---|---|---|
| `04/audit-prompt.md` | point the architect at a repo | fable / best |
| `05/plan.template.md` | ordered steps, one owner each | fable / best |
| `06/handoff.template.md` | carry a decision to any executor | sonnet |
| `10 /architect` | classify a task, route to a seat | fable / best |
| `03/estimate.py` | price a task before you run it | none |

## When the next flagship lands

Don't trust its launch benchmarks, and don't trust the "it's basically Fable at half the price" takes that flood the timeline within a day. Measure it on your work: seat it, meter it, curve it, update the roster, and keep it only if the receipt says so. That routine is written down in [adopt-next.md](adopt-next.md), because a habit that lives in your head doesn't survive you.

While you're in there, do one subtraction. **Strip the workarounds.** Every "never do X" you accumulated fighting the old model is a candidate bug in the new one, and Anthropic's own team tells that story on themselves: a stale citation-format instruction sat harmlessly in a system prompt until a better-instruction-following model started *obeying* it. Prune before you tune.

## About the other repo

The book has you assemble `model-team/` by hand, out of your own artifacts, as you go. That one is yours. This one is the reference you clone from: the same artifacts, pre-assembled and runnable, so you can hold yours up against a working one.
