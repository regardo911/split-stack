# 03 · Estimate a task before you run it

Four dollars. That was the bill for a five-line rounding fix, because Fable read a quarter of the repo to get there. The arithmetic is not complicated, and once it's a tool you can answer *"what will this cost"* for any task on any seat in about a second.

Price a real job with your own token counts:

```bash
python3 estimate.py --model sonnet-5 --input 15000 --output 3000
python3 estimate.py --compare --input 250000 --output 30000    # every seat, one job
python3 estimate.py --seats                                     # the roster table
```

`--compare` on 250K in / 30K out is the Chapter 1 bug fix. It comes back $4.00 on Fable and $0.40 on Haiku. Same keystrokes.

## The two levers

Both are flags, and neither touches a routing decision:

```bash
python3 estimate.py --model fable-5 --input 150000 --output 12000            # $2.10 cold
python3 estimate.py --model fable-5 --input 150000 --output 12000 --batch    # half
python3 estimate.py --model fable-5 --input 150000 --output 12000 --cache-read 140000
```

Batch halves everything. A cached prefix reads at a tenth. The $2.10 audit lands at $0.84 without moving a single task to a different seat.

## Your numbers, not mine

Get real token counts off a trace instead of guessing at them:

```bash
claude -p --output-format json "your task" > run.json
```

Feed those into `--compare` and read what the same job would have cost on each seat. That gap *is* the routing decision, priced.

Everything this prints is a **worked estimate**: arithmetic over published rates. The word *receipt* is reserved for metered spend read off a real trace, and Chapter 11 is where you get one.
