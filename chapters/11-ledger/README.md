# 11 · The three-way ledger

*"Has anyone actually compared total tokens for the same task between Fable and Opus?"*

A hundred and one upvotes. Not one real answer in the thread. It is the most-asked, never-answered question in this entire topic, and the reason nobody answers it is that answering it requires shipping the same feature three times and reading the meter honestly, including when the meter says something you don't like.

This tool will not accept a made-up number.

## Ship it three times

Reset hard between runs. A warm cache or a half-applied diff makes the ledger lie:

```bash
git stash                                                  # or a fresh branch off the same commit
claude -p --output-format json "..." > traces/split.json
```

Then write down the parts only you can see, and read it:

```bash
cat > my-runs.json <<'EOF'
[
  {"config": "split-stack", "trace": "traces/split.json", "wall_clock_min": 18, "cross_file_bug_caught": true},
  {"config": "all-Fable",   "trace": "traces/fable.json", "wall_clock_min": 30, "cross_file_bug_caught": true},
  {"config": "all-Opus",    "trace": "traces/opus.json",  "wall_clock_min": 22, "cross_file_bug_caught": false}
]
EOF

python3 ledger.py my-runs.json
```

Cost is read from the trace. **Wall-clock and bug-caught are yours.** They come from watching a real run, not from token pricing, so if you leave them out the ledger prints `unknown, you must observe this` rather than inventing one for you. It will not judge a run nobody watched.

## Expect it to be uncomfortable

On a feature with a real cross-file bug in it, all-Opus tends to come in **cheapest on the meter and ship the bug**. The split-stack costs about forty cents more and catches it.

That is not a bug in the ledger. The ledger prices tokens; it does not price the bug. That forty cents buys Fable-grade judgment on the audit, and on a task with no lurking trap it buys you nothing but reassurance. A bug you never shipped has no line item.

The one result that holds on every axis, every time: **never let Fable type.** All-Fable loses on cost *and* on the clock, because the seat you're overpaying is also the seat that's rate-limited to a sip.

## The book's own numbers

```bash
python3 ledger.py --example
```

Those are **worked estimates**, modelled from published rates. Arithmetic you can reproduce line by line, not money anyone was billed. They show you the shape of the three-way choice. Your traces are the only receipt.
