#!/usr/bin/env python3
"""estimate.py -- Chapter 3. Price a task before you hit Enter.

Feed it YOUR token counts. It prices them on any seat, on every seat, or prints
the roster table. Cached reads bill at a tenth; batch halves everything.

    estimate.py --model sonnet-5 --input 15000 --output 3000
    estimate.py --model fable-5 --input 150000 --output 12000 --cache-read 140000
    estimate.py --model fable-5 --input 150000 --output 12000 --batch
    estimate.py --compare --input 250000 --output 30000
    estimate.py --seats

Every number this prints is a WORKED ESTIMATE: arithmetic over published rates.
It is not a receipt. A receipt is metered spend read off a real trace
(`claude -p --output-format json`) -- that is what chapters/11-ledger reads.

Stdlib only, offline, zero keys. Standalone by design: the RATES dict is repeated
in the other chapter scripts on purpose, so each file is copy-pasteable alone.
"""

import argparse

# Rates are $ per million tokens (input, output).
RATES = {
    "fable-5":   (10, 50),
    "opus-4-8":  (5, 25),
    "sonnet-5":  (3, 15),
    "haiku-4-5": (1, 5),
}


def cost(model, tok_in, tok_out, cache_read=0, batch=False):
    rin, rout = RATES[model]
    fresh_in = tok_in - cache_read              # cached reads bill at 10%
    dollars = (fresh_in * rin + cache_read * rin * 0.1 + tok_out * rout) / 1_000_000
    return dollars * 0.5 if batch else dollars  # batch halves everything


# The seat names, in roster order. Same four rates, spelled the way the book's
# roster table spells them.
SEATS = [
    ("fable-5",   "Fable 5",   "architect -- judgment only"),
    ("opus-4-8",  "Opus 4.8",  "heavy specialist / Fable's fallback target"),
    ("sonnet-5",  "Sonnet 5",  "primary executor -- your default typist"),
    ("haiku-4-5", "Haiku 4.5", "cheap typist -- bounded mechanical work"),
]


def print_seats():
    """The roster table, proved from the rates instead of retyped."""
    fable_out = RATES["fable-5"][1]
    print(f"{'seat':11} {'model id':11} {'$in/$out per MTok':>18}  {'out vs Fable':>12}  role")
    for key, name, role in SEATS:
        r_in, r_out = RATES[key]
        rate = f"${r_in}/${r_out}"
        print(f"{name:11} {key:11} {rate:>18}  {r_out / fable_out:>11.1f}x  {role}")
    print("\nsame keystrokes, "
          f"{RATES['fable-5'][1] / RATES['haiku-4-5'][1]:.0f}x apart: architect vs typist")
    print("worked estimate from published rates -- not a metered receipt.")


def print_one(model, tok_in, tok_out, cache_read, batch):
    fresh = tok_in - cache_read
    r_in, r_out = RATES[model]
    total = cost(model, tok_in, tok_out, cache_read, batch)
    print(f"{model}  ({tok_in} in / {tok_out} out"
          f"{f', {cache_read} cached' if cache_read else ''}{', batched' if batch else ''})")
    print(f"  fresh input : {fresh:>9} @ ${r_in}/M")
    if cache_read:
        print(f"  cached read : {cache_read:>9} @ ${r_in * 0.1:g}/M   (a tenth)")
    print(f"  output      : {tok_out:>9} @ ${r_out}/M")
    print(f"  TOTAL       : ${total:.4f}" + ("   (batch: everything halved)" if batch else ""))

    if (batch or cache_read) and total:
        cold = cost(model, tok_in, tok_out)
        print(f"  cold+uncached it would be ${cold:.4f}  -> the levers cut it "
              f"{cold / total:.1f}x, and touched no routing decision")
    if model != "fable-5" and total:
        on_fable = cost("fable-5", tok_in, tok_out, cache_read, batch)
        print(f"  on fable-5 the same job bills ${on_fable:.4f}  -> "
              f"Fable would bill {on_fable / total:.1f}x")
    print("\nworked estimate from published rates -- not a metered receipt.")


def print_compare(tok_in, tok_out, cache_read, batch):
    print(f"the same job ({tok_in} in / {tok_out} out"
          f"{f', {cache_read} cached' if cache_read else ''}{', batched' if batch else ''}) "
          "on every seat:\n")
    prices = {k: cost(k, tok_in, tok_out, cache_read, batch) for k, _, _ in SEATS}
    cheapest = min(prices, key=prices.get)
    fable = prices["fable-5"]
    print(f"{'seat':11} {'cost':>9}  {'vs Fable':>9}")
    for key, name, _ in SEATS:
        c = prices[key]
        mult = f"{fable / c:.1f}x cheaper" if c and c < fable else "--"
        print(f"{name:11} {c:>9.4f}  {mult:>16}"
              + ("   <- cheapest" if key == cheapest else ""))
    print(f"\nrouting this job down from fable-5 to {cheapest} saves "
          f"${fable - prices[cheapest]:.4f} on this one task.")
    print("Is it judgment (worth frontier money) or typing (route it down)?")
    print("worked estimate from published rates -- not a metered receipt.")


def main():
    p = argparse.ArgumentParser(
        description="Price a task on the four seats, from your own token counts.",
        epilog="Get real token counts off a trace: claude -p --output-format json 'task'",
    )
    p.add_argument("--model", choices=sorted(RATES), help="price the job on one seat")
    p.add_argument("--compare", action="store_true", help="price the same job on all four seats")
    p.add_argument("--seats", action="store_true", help="print the roster table and exit")
    p.add_argument("--input", type=int, default=0, metavar="TOK", help="input tokens")
    p.add_argument("--output", type=int, default=0, metavar="TOK", help="output tokens")
    p.add_argument("--cache-read", type=int, default=0, metavar="TOK",
                   help="how many of the input tokens are cached reads (bill at 10%%)")
    p.add_argument("--batch", action="store_true", help="batch endpoint: halves everything")
    a = p.parse_args()

    if a.seats:
        print_seats()
        return 0
    if not a.model and not a.compare:
        p.error("give --model MODEL, or --compare, or --seats")
    if a.input <= 0 and a.output <= 0:
        p.error("give the job's token counts: --input and --output")
    if a.cache_read > a.input:
        p.error(f"--cache-read {a.cache_read} exceeds --input {a.input}: "
                "cached reads are a subset of the input tokens")

    if a.compare:
        print_compare(a.input, a.output, a.cache_read, a.batch)
    else:
        print_one(a.model, a.input, a.output, a.cache_read, a.batch)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
