<!--
audit-prompt.md — Chapter 4 / Appendix A1. The four-phase, analysis-only repo
audit that keeps Fable in the judgment lane (Fable points; the cheap seats shoot).

Run it from inside the repo you want audited:
    claude --model fable --effort high "$(cat audit-prompt.md)" > audit.md

This file is a PROMPT, not runnable code. It needs a paid Claude account to run;
a worked output ships at ../../worked-examples/audit.md so the
figures and greps have real audit output to point at offline.
-->

You are a senior staff engineer auditing this repository. Do NOT edit any
files. Your entire output is a written report. Ground every single claim in
a specific file:line reference. If you cannot point to a line, do not make
the claim.

Work in four phases and label them in your output.

## Phase 1 — Discovery
Map the codebase before judging it. List the entry points, the main data
flow, the external boundaries (APIs, webhooks, the database, third-party
calls), and where untrusted input enters the system.

## Phase 2 — Audit
Find real problems. For each finding, give exactly:
  - WHAT: the problem, in one sentence
  - WHERE: file:line
  - WHY: the concrete consequence if left alone
  - SEVERITY: P0 (ships-broken / security) · P1 (serious) · P2 (should fix)
    · P3 (nit)
Do not pad the list. A short list of real P0s beats a long list of P3s.

## Phase 3 — Improvement strategy
Group the findings into themes (e.g., "input validation," "error handling").
For each theme, state the shape of the fix in two sentences.

## Phase 4 — Task plan
Turn the findings into an ordered task list. For each task give:
  - a size: S / M / L / XL
  - a milestone bucket: M0 (do now) · M1 · M2 · M3
  - an OWNER MODEL: the cheapest model that can safely execute this fix.
    Use Haiku for mechanical edits, Sonnet for specified logic, Opus or
    Fable ONLY where the fix itself requires real judgment.

Output the whole report as markdown.

---

## Scope block (append when the repo is bigger than your context)
Paste this under the phase instructions for a monorepo-scale audit so the run
writes its evidence down instead of trying to hold everything in memory:

```markdown
## Budget (this repo is bigger than your context — obey these caps)
- Never read a file end to end: at most 150 lines per file, 200 files total.
- Sweep everything else with grep instead of reading it.
- After every 25 files, append findings to audit-evidence.md and drop the
  raw text from your working memory.
- Every claim in audit-evidence.md carries a file:line receipt.
```

To narrow a large repo to where the money and risk live, add a one-line focus:

```markdown
Restrict this audit to the payments and webhook code paths
(src/webhooks/, src/billing/, and anything they call). Ignore the rest.
```

---

## Variant A — audit your instruction files (config audit)
Point Fable at the files that tell your stack how to behave. They rot silently,
and a stale rule breaks every run until you catch it.

```markdown
Audit my instruction files (CLAUDE.md, .claude/agents/*, README, and any
setup docs) as if you were a new engineer who must follow them literally.
Do NOT edit anything. Report, with file:line:
  - Contradictions: two rules that can't both be satisfied
  - Stale rules: instructions that reference files, flags, or commands
    that no longer exist
  - Gaps: decisions a new hire would have to guess because no rule covers them
Rank each by how much damage it does if followed blindly.
```

---

## Variant B — point it at your own blind spots (blindspot pass)
Run before working in a subsystem you don't know. The findings are holes in
your map instead of holes in the code.

```markdown
I'm adding a new SSO auth provider but I've never touched the auth module.
Do a blindspot pass: find my unknown unknowns in this part of the codebase,
explain each one, and tell me how to prompt you better for the implementation.
```

A good blindspot card:

```markdown
### Blindspot — the auth "template" that isn't one
- WHAT YOU DIDN'T KNOW: saml/handler.ts looks like the file to copy, but it
  deliberately bypasses authPipeline. Copy it and session checks never run.
- RECEIPT: src/auth/saml/handler.ts, and the revert of PR #2841
- PROMPT FIX: "Use oauth/google.ts as the structural template, not
  saml/handler.ts. Confirm the new provider's routes mount inside
  authPipeline and show me the mount point."
```
