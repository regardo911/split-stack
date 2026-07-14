# Errata & reconciliation

The printed book is a fixed snapshot; this repository is live and gets maintained. When
the two disagree, this file is the tie-breaker. It has two parts: **corrections**, where
the book is simply wrong, and **reconciliation**, where the repo has moved past the pages
and you just need the two lined up. Code changes to the repo are logged in `CHANGELOG.md`.

---

## Corrections (the printed book is wrong)

### Appendix A6: the fallback check reads a field that doesn't exist

The first item of the "Fallback-detection checklist" prints:

```bash
claude -p --model fable --output-format json ... | jq '.model'
```

There is no top-level `.model` on the Claude Code JSON envelope; that field returns
`null`, so the check never fires. Read the served model from `.modelUsage` instead,
taking the entry that did the real work (the highest-cost key):

```bash
served=$(claude -p --model fable --output-format json "your task" \
  | jq -r '.modelUsage | to_entries | max_by(.value.costUSD) | .key')
[ "$served" = "claude-fable-5" ] || echo "WARNING: $served served this, not Fable" >&2
```

This is the form the Chapter 9 body already uses, and it's what
`chapters/09-fallback/fallback.py` implements. Use it in place of the Appendix A6 line.

### Chapter 4: the sample SAML finding cites a PR that isn't here

The worked audit finding for the SAML bug lists "the revert of PR #2841" as its receipt.
That PR number is illustrative. The demo app in this repo has a linear history and no such
PR, so don't go looking for it in the git log. The bug itself is real and still in the
code: see `demo/invoicing-api/SPOILERS.md`, bug #6 (`src/auth/saml/handler.ts`).

---

## Reconciling the book with the current repo

### The chapter scripts take your input; the printed runs show a fixed example

In the book, `route.py`, `estimate.py`, and `ledger.py` each print one canned run
("run it and you'll see..."). In this repo they read *your* numbers rather than shipping a
frozen answer, so a bare run asks for input instead of reprinting the book's figures. To
reproduce exactly what the pages show:

- **`route.py`** routes one task per run from flags
  (`--judgment`/`--mechanical`/`--fresh`); the book's five-row table is the `tasks = [...]`
  list inside the Chapter 2 listing. The Chapter 2 output-cost table and 50K-token receipt
  are reproduced verbatim by **`roster.py`** (added to `chapters/02-route-a-task/`); run
  `python3 roster.py`.
- **`estimate.py`**: pass `--model MODEL`, `--compare`, or `--seats`. A bare run prints
  usage rather than a fixed dollar figure.
- **`ledger.py`**: run `python3 ledger.py --example` to get the Chapter 11 figures
  ($1.86 split-stack / $2.95 all-Fable / $1.47 all-Opus). A bare run wants your own runs
  file.

### The demo app is more compact than the book's excerpts

`demo/invoicing-api` was tightened for the repo, so the `file:line` citations in
Chapters 4, 8, and 10 point at line numbers from a longer draft. Every seeded bug is still
present and reachable at runtime; only the coordinates moved. The current, exact locations
are in `demo/invoicing-api/SPOILERS.md`.

One finding no longer reads as printed: `src/webhooks/verify.ts` ships complete and
correct (HMAC-SHA256 with a length guard and a constant-time compare). The exercise is
that the webhook handler never *calls* it (SPOILERS bug #1), not that the helper is
missing or unguarded. Chapters 5 and 6 have you build `verifySignature` from scratch; in a
clone it already exists, so the remaining work is to wire it into the handler.

### Chapter 12: cloning vs. retyping the `model-team/`

The Chapter 12 build step assembles a `model-team/` directory by copying files with flat
paths (`cp ../audit-prompt.md ../plan.md ...`). Those are *your own* artifacts from the
Chapter 3 through 12 build steps, laid out flat the way the book has you build them. For
the retype-as-you-read reader, the block is correct as written.

If you are instead assembling `model-team/` from a **clone**, this repo is organized one
folder per chapter, so the sources live under `chapters/NN-*/` (and three carry a
`.template` suffix):

| Chapter 12 `cp` source | In this repo |
|---|---|
| `../audit-prompt.md` | `chapters/04-audit-a-repo/audit-prompt.md` |
| `../plan.md` | `chapters/05-write-a-plan/plan.template.md` |
| `../handoff.md` | `chapters/06-handoff/handoff.template.md` |
| `../estimate.py` | `chapters/03-estimate-a-task/estimate.py` |
| `../roster.py` · `../route.py` | `chapters/02-route-a-task/roster.py` · `route.py` |
| `../adopt-next.md` | `chapters/12-portable-team/adopt-next.md` |
| `../.claude/skills/architect` | `skill/architect/` (installed to `~/.claude/` by `install.sh`) |

The appendix's file tree shows the chapter-facing layout. The repo also ships the ordinary
top-level files a runnable project needs and the appendix doesn't list: `README.md`,
`GOTCHAS.md`, this `ERRATA.md`, `CHANGELOG.md`, `Makefile`, `LICENSE`, `tests/`, `docs/`,
and CI.
