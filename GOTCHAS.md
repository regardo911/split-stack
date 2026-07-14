# Gotchas

Things that actually bit while building this, written down so they don't bite you.
None of these are hypothetical. Each one cost somebody an afternoon.

## `curl -d @file` never reaches an `express.raw({ type: "application/json" })` handler

The webhook has to see the **raw bytes** to verify a signature, so it's mounted with
`express.raw()` before the JSON body parser. The obvious content-type filter is
`{ type: "application/json" }`, and it looks right.

But `curl -X POST -d @forged.json` sends `application/x-www-form-urlencoded`, not JSON.
The raw parser skips the body entirely, the handler gets an empty buffer, and the
forged-POST gate in Chapter 6 quietly fails to test anything at all.

`src/server.ts` uses `{ type: "*/*" }` so the exact `curl` the book prints actually
reaches the handler. If you tighten that filter, tighten the curl too.

## `node --test dist/**/*.test.js` silently matches nothing on Node 20

Recursive `**` globbing in the test runner needs Node 22. On Node 20 that pattern
doesn't error. It matches zero files, the runner reports success, and CI goes green
having run **no tests**.

That's the worst kind of failure: a passing build that proves nothing. `package.json`
spells the paths out (`dist/*.test.js dist/*/*.test.js`) instead of trusting the glob.
If you add a test three directories deep, add the path.

## The demo app lets you read invoices with no auth, on purpose

`src/auth/mw.ts` has an `allowAnonymousReads` escape: an unauthenticated GET falls
back to a read-only session so `curl localhost:3000/invoices` works with no identity
provider, no token, and no setup.

**That is a demo affordance and it would be a vulnerability in a real service.** It's
called out here rather than buried, because a reader auditing this app deserves to
know which holes were left open deliberately and which ones are the exercise. This one
is deliberate. The others are not.

## There is no top-level `.model` on the Claude Code JSON envelope

The natural way to check which seat served a headless run is
`claude -p --output-format json ... | jq '.model'`. It returns `null`. The CLI wraps
the reply in a result envelope, and the served model lives in `.modelUsage`, keyed by
model, where the entry that did the real work is the one with the highest `costUSD`.
A cheap housekeeping model can show up in there too, which is why you take the max
rather than the first key.

`chapters/09-fallback/fallback.py` reads it correctly, and so does the `served=...`
snippet in Chapter 9. If you are working from the Appendix A6 checklist, reach for the
`.modelUsage` form above instead of `jq '.model'` — that correction is in `ERRATA.md`.

## The scripts are standalone on purpose, and that is not laziness

There is no `pyproject.toml`, no package, no shared `rates.py`. The four-line rate table
is repeated in every script that needs it.

The first version of this repo *did* have packaging, and it broke CI immediately:
setuptools auto-discovery found several top-level directories, refused to guess which
one was the package, and failed the install. A local virtualenv masked it completely,
because only a clean `pip install` reproduces it.

The deeper reason is the reader, not the bug. The book prints each script standalone.
You should be able to copy one out of here into your own repo and have it run, with no
import to satisfy and nothing to install. Duplicating four lines of a rate table is a
much smaller cost than a package that has to be built before anything works.

## A rewritten `.gitignore` nearly committed a 3,728-file virtualenv

While cutting the old figure generator, its `.venv` (Pillow, matplotlib, the works)
was still sitting in the working tree. The rewritten `.gitignore` dropped the `.venv/`
rule, and `git add -A` happily staged all 3,728 files.

It got caught in the second before the commit, by looking at the staged count rather
than trusting the pattern. If you rewrite an ignore file wholesale, diff the staged
file count against what you expect. Do not just glance at the rules.
