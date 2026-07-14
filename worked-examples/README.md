# Worked examples

Inputs to feed the chapter tools, and the book's own modeled numbers. All of it is
**illustrative** — arithmetic over published rates, or a sample artifact. None of it
is a **receipt**: that word is reserved for metered spend read off a real trace
(`claude -p --output-format json`). Your own runs are the only receipt.

| File | Chapter | What it is |
|---|---|---|
| `book-ledger.json` | 11 | The three runs, **modeled** — cost, wall-clock, bug-caught. `ledger.py --example` reads it. |
| `audit.md` | 4 | A Fable audit of the demo repo. |
| `plan.md` | 5 | The webhook plan. Input to `plan-check.sh`. |
| `handoff.md` | 6 | The handoff contract. Input to `contract-lint.js`. |
| `verdict.md` / `verdict-clean.md` | 8 | A graded verdict that sends back, and one that ships. Input to `gate.sh`. |
| `changed.txt` | 8 | A changed-files list. Input to `needs-senior.sh`. |
| `refusals/*.json` | 9 | The five refusal categories, a fallback receipt shape, and a skipped fallback. Input to `fallback.py`. |
