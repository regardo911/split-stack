# split-stack

**Route judgment to the expensive seat. Route typing to the cheap one. Never let the
architect touch the keyboard.**

The companion toolkit to [*Claude Fable 5: Turn One Model Into a Team*](https://youcanbuildthings.com).
The artifacts you build in the book, ready to install, plus a real application to
practise them on.

The book explains. This gives you the files, the commands, and something real to
point them at.

---

## Start here, fifteen minutes

**1. Install the router.** Thirty seconds, no API key.

```bash
git clone https://github.com/regardo911/split-stack.git
cd split-stack
./install.sh
```

That puts the `/architect` skill and the Sonnet-pinned `executor` sub-agent into
`~/.claude/`. It now works in **every project on your machine**, because routing logic
is universal and doesn't belong to one repo.

**2. Bring up the app you're going to audit.** Two minutes, no key, no database.

```bash
cd demo/invoicing-api
npm install && npm test
```

This is the mid-size TypeScript billing service the book breaks in every chapter. It
compiles, it boots, and **its tests pass while real bugs are still sitting in it.**

That's not sloppiness. It's the book's own thesis: those bugs are correct in isolation
and only wrong in composition, which is exactly the class of bug a unit test cannot see
and a whole-repo audit can. Finding them is the exercise.

**3. Route a real task.** Needs Claude Code, which is the tool you bought this book to
use better. From inside `demo/invoicing-api`:

```
/architect the reconciliation job double-charges intermittently; find the cause and fix it
```

You should get back a `MIXED` classification, a real diagnosis from the architect seat,
a written handoff, and **a cheap-seat command to run the fix**. Not the fix itself. If
it typed the fix on Fable, the router is broken.

**4. Point it at your own repo.** `/architect` is already installed globally. Go run it
on a task you actually care about. That transfer is the whole book.

---

## The chapters

Each folder is one chapter: what you build, one command, what success looks like, and
how to point the same artifact at your own project.

| | Build | Run |
|---|---|---|
| [02](chapters/02-route-a-task/) | the routing rule, as code | `route.py --judgment no --mechanical yes` |
| [03](chapters/03-estimate-a-task/) | what a task costs, before you run it | `estimate.py --compare --input 250000 --output 30000` |
| [04](chapters/04-audit-a-repo/) | the four-phase audit prompt | `claude -p --model fable "$(cat audit-prompt.md)"` |
| [05](chapters/05-write-a-plan/) | `plan.md`, five fields per step | `plan-check.sh plan.md` |
| [06](chapters/06-handoff/) | the handoff contract | `node contract-lint.js handoff.md` |
| [07](chapters/07-delegate/) | the delegation brief and the spend cap | `claude -p --max-budget-usd 5 …` |
| [08](chapters/08-review/) | one graded review pass | `gate.sh verdict.md` |
| [09](chapters/09-fallback/) | catch the silent Opus fallback | `fallback.py run.json --expect claude-fable-5` |
| [10](chapters/10-architect/) | **`/architect`, the router** | `/architect <task>` |
| [11](chapters/11-ledger/) | the three-way ledger | `ledger.py my-runs.json` |
| [12](chapters/12-portable-team/) | the swap drill | `adopt-next.md` |

Also here: [`demo/invoicing-api`](demo/invoicing-api/) (the app you audit),
[`skill/`](skill/) (what `install.sh` installs),
[`worked-examples/`](worked-examples/) (the book's modelled numbers and sample
artifacts), [`docs/architecture.md`](docs/architecture.md) (the whole loop, one
diagram), and [`GOTCHAS.md`](GOTCHAS.md) (the things that bit us, so they don't bite
you).

---

## What runs without an API key

Everything under `chapters/` is a plain script. Python stdlib, Node built-ins, POSIX
shell. No keys, no accounts, no network, nothing to install. `demo/invoicing-api` needs
`npm install` once, and still no keys, no accounts, no database.

**`/architect` is the exception.** It is a Claude Code *skill*: an instruction file the
harness reads and follows, so it needs Claude Code and a model. It is **not** a local
routing engine, and **nothing here tests its judgment.** Chapter 10 spells out exactly
what that does and does not mean.

## Two words this repo uses carefully

A **worked estimate** is arithmetic over published rates. `estimate.py`, `route.py`, and
everything in `worked-examples/` produce worked estimates.

A **receipt** is metered spend read off a real trace (`claude -p --output-format json`).
`ledger.py` reads receipts, and it will not invent your wall-clock time or whether a bug
got caught, because those are observations only you can make.

The book's rule was *show me the receipt*. A modelled number is not one.

## Contributing

Fixes welcome. New features are out of scope: this repo mirrors a book on purpose. Fork
it and make it yours. It's a starting point, not a maintained library.

MIT. Educational software, provided as-is, no warranty. From
[youcanbuildthings.com](https://youcanbuildthings.com).
