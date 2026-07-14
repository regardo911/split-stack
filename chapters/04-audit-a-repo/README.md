# 04 · Audit a repo

Do not let it fix anything.

That's the whole discipline of this chapter. The most valuable thing the architect seat does is read your entire codebase and tell you, ranked, what's wrong with it. The instant it stops judging and starts editing files, you are paying frontier rates for work a cheaper seat should do. So the prompt is analysis-only, and it ends by naming which cheap seat fixes each thing.

Run it against the demo app, which has real bugs its own passing tests never see:

```bash
cd ../../demo/invoicing-api
claude -p --model fable --effort high "$(cat ../../chapters/04-audit-a-repo/audit-prompt.md)" > audit.md
```

Open `audit.md`. Four labelled phases. Phase 1 maps the system before it judges it (entry points, data flow, where untrusted input gets in) and it is the part everyone skips. Don't: it's the trust gauge. If the map is right, the findings under it are probably real. Phase 4 assigns every fix an owner model, so the expensive seat has already done the only expensive part.

## Three questions that kill a fake finding

Fable can over-read, over-think, and hand you a beautifully formatted list of nothing. Run every P0 and P1 through these, and delete what fails:

1. Go to the `file:line`. Is the problem actually sitting there, or is it a hallucination wearing a line number?
2. Is the WHY a real consequence (money, a security hole, an outage), or is it "improves maintainability"?
3. Would you fix it if a senior engineer flagged it in review?

What survives is your backlog. If the P0s don't survive, don't rerun it hoping for a better answer. Re-scope it, or accept the clean bill.

Only after you've done your own pass, check yourself against [SPOILERS.md](../../demo/invoicing-api/SPOILERS.md). It's the answer key, and reading it first wastes the exercise.

## On your own repo

Same command, twenty minutes. If the repo is large, point it at one subsystem at a time. Scope is the whole difference between a $1.60 audit that finds the webhook hole and a $12 audit that finds forty style nits.
