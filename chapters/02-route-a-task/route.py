#!/usr/bin/env python3
"""route.py -- Chapter 2. The one rule as code: judgment up, typing down.

Answer three questions about YOUR task and it names the seat, plus the overpay
you'd have burned by leaving it on the architect.

    route.py --judgment no --mechanical yes --fresh no   -> Haiku 4.5
    route.py --judgment yes                              -> Fable 5
    route.py --judgment no --mechanical no --fresh no    -> Sonnet 5

Flags take yes/no (also y/n, true/false, 1/0). Unset means no.

Stdlib only, offline, zero keys. Standalone by design.
"""

import argparse

# Output rates ($/MTok) price what each misroute to Fable would have cost.
OUT = {"Fable 5": 50, "Sonnet 5": 15, "Haiku 4.5": 5}


def route(needs_judgment, mechanical, needs_fresh_fact):
    if needs_judgment:
        return "Fable 5"            # a decision -> the architect
    if mechanical and not needs_fresh_fact:
        return "Haiku 4.5"          # bounded typing, no fresh fact -> cheapest seat
    return "Sonnet 5"               # a build, or typing that needs a fresh fact


WHY = {
    "Fable 5":   "a decision is on the line -- pay for the best brain",
    "Haiku 4.5": "bounded typing, no fresh fact needed -- cheapest seat that types it right",
    "Sonnet 5":  "a build, or typing that needs a fresh fact -- your default typist",
}


def yesno(value):
    v = value.strip().lower()
    if v in ("yes", "y", "true", "t", "1"):
        return True
    if v in ("no", "n", "false", "f", "0"):
        return False
    raise argparse.ArgumentTypeError(f"expected yes or no, got {value!r}")


def main():
    p = argparse.ArgumentParser(
        description="Place one task on a seat: judgment up, typing down.",
        epilog="Split a task that is really two ('diagnose the bug, then fix it') "
               "into two runs -- diagnosis is judgment, the fix is typing.",
    )
    p.add_argument("--judgment", type=yesno, default=False, metavar="yes|no",
                   help="is there a real decision to make? (default no)")
    p.add_argument("--mechanical", type=yesno, default=False, metavar="yes|no",
                   help="is it bounded, repetitive typing? (default no)")
    p.add_argument("--fresh", type=yesno, default=False, metavar="yes|no",
                   help="does it need a fact newer than the cheap seat's cutoff? (default no)")
    p.add_argument("--task", default="", metavar="TEXT", help="optional label for the printout")
    a = p.parse_args()

    seat = route(a.judgment, a.mechanical, a.fresh)
    waste = OUT["Fable 5"] / OUT[seat]
    note = "keep on Fable" if seat == "Fable 5" else f"Fable would bill {waste:.1f}x"

    label = a.task or "this task"
    yn = {True: "yes", False: "no"}
    print(f"judgment={yn[a.judgment]}  mechanical={yn[a.mechanical]}  fresh={yn[a.fresh]}")
    print(f"{label:35.35} -> {seat:10} {note}")
    print(f"  {WHY[seat]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
