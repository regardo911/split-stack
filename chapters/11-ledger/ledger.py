#!/usr/bin/env python3
"""ledger.py -- Chapter 11. Three real runs, one honest three-way ledger.

    ledger.py my-runs.json
    ledger.py --example            # the book's MODELED numbers, clearly banner'd

my-runs.json is a list of the runs YOU shipped:

    [
      {"config": "split-stack", "trace": "traces/split.json",
       "wall_clock_min": 18, "cross_file_bug_caught": true},
      {"config": "all-Opus",    "cost_usd": 1.47}
    ]

Cost comes off the trace -- a real `claude -p --output-format json` result object.
It prefers the documented `total_cost_usd` field and falls back to summing
`modelUsage[].costUSD`, and it tells you which one it used. A `cost_usd` you typed
in by hand is accepted and LABELLED as hand-entered.

Wall-clock and cross-file-bug-caught are NOT derivable from token pricing. They
are observations only you can make on a real run. If they are missing this prints
"unknown -- you must observe this". It will never guess one for you.

Stdlib only, offline, zero keys. Standalone by design.
"""

import argparse
import json
import os
import sys

UNKNOWN = "unknown -- you must observe this"

# The columns whose values no arithmetic can produce.
OBSERVED_FIELDS = ("wall_clock_min", "cross_file_bug_caught")


def cost_from_trace(trace):
    """Read the real cost off a `claude -p --output-format json` result object.

    Returns (dollars, source). Inspects BOTH documented places and prefers the
    top-level field; reports which one it read.
    """
    documented = trace.get("total_cost_usd")
    per_model = trace.get("modelUsage")
    summed = None
    if isinstance(per_model, dict) and per_model:
        summed = sum((v or {}).get("costUSD") or 0 for v in per_model.values())

    if isinstance(documented, (int, float)):
        source = "trace: total_cost_usd"
        if summed is not None and abs(summed - documented) > 0.005:
            source += f" (note: modelUsage[].costUSD sums to ${summed:.2f} instead)"
        return float(documented), source
    if summed is not None:
        return float(summed), "trace: summed modelUsage[].costUSD (no total_cost_usd field)"
    raise ValueError("no total_cost_usd and no modelUsage[].costUSD in this trace")


def resolve(path, base_dir):
    """Trace paths resolve against the cwd first, then the runs file's directory."""
    if os.path.isabs(path) or os.path.exists(path):
        return path
    return os.path.join(base_dir, path)


def load_runs(path):
    """Read the runs file. Accepts a bare list, or {"runs": [...]} with a note."""
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("runs") or [], data.get("_note")
    return data, None


def price(run, base_dir):
    """Return (dollars, source_label) for one run. Never invents a number."""
    if run.get("trace"):
        trace_path = resolve(run["trace"], base_dir)
        with open(trace_path) as f:
            trace = json.load(f)
        dollars, source = cost_from_trace(trace)
        return dollars, source
    if isinstance(run.get("cost_usd"), (int, float)):
        return float(run["cost_usd"]), "hand-entered (not read from a trace)"
    raise ValueError(f"run {run.get('config')!r} has neither a trace nor a cost_usd")


def observed(run, field):
    """An observation, or the honest UNKNOWN. Never a guess."""
    value = run.get(field)
    return UNKNOWN if value is None else value


def render(runs, base_dir):
    rows = []
    for run in runs:
        name = run.get("config") or "(unnamed)"
        dollars, source = price(run, base_dir)
        rows.append({
            "config": name,
            "cost": dollars,
            "source": source,
            "wall_clock_min": observed(run, "wall_clock_min"),
            "cross_file_bug_caught": observed(run, "cross_file_bug_caught"),
        })

    print(f"{'config':14} {'$ cost':>8}  {'min':>7}  {'bug caught':>11}  cost read from")
    for r in rows:
        mins = r["wall_clock_min"]
        mins = "unknown" if mins == UNKNOWN else str(mins)
        bug = r["cross_file_bug_caught"]
        bug = "unknown" if bug == UNKNOWN else str(bug)
        print(f"{r['config']:14} {r['cost']:>8.2f}  {mins:>7}  {bug:>11}  {r['source']}")

    if any(r["wall_clock_min"] == UNKNOWN or r["cross_file_bug_caught"] == UNKNOWN
           for r in rows):
        print(f"\n'unknown' means exactly that: {UNKNOWN}.")
        print("Wall-clock and bug-caught come from watching a real run, not from token pricing.")

    cheapest = min(rows, key=lambda r: r["cost"])
    print(f"\ncheapest by cost: {cheapest['config']} (${cheapest['cost']:.2f})")

    shipped = [r["config"] for r in rows if r["cross_file_bug_caught"] is False]
    unobserved = [r["config"] for r in rows if r["cross_file_bug_caught"] == UNKNOWN]
    print(f"shipped the cross-file bug: {shipped or 'none of the observed runs'}")
    if unobserved:
        print(f"  (not observed, so not judged: {', '.join(unobserved)})")

    if shipped and cheapest["config"] in shipped:
        print("\nThe cheapest run shipped the bug. The ledger prices tokens; it does not "
              "price the bug. Read it as a floor on the decision, never the ceiling.")
    return 0


EXAMPLE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "..", "worked-examples", "book-ledger.json")


def main():
    p = argparse.ArgumentParser(
        description="Turn three real runs into one honest three-way ledger.",
        epilog="Capture a run: claude -p --output-format json 'task' > traces/split.json",
    )
    p.add_argument("runs", nargs="?", help="JSON list of your runs")
    p.add_argument("--example", action="store_true",
                   help="run against the book's modeled numbers (worked estimates, not receipts)")
    a = p.parse_args()

    if a.example:
        path = os.path.normpath(EXAMPLE)
        print("=" * 78)
        print("WORKED ESTIMATES -- modeled from published rates, NOT metered receipts.")
        print("Every cell is arithmetic you can reproduce; none of it was billed to anyone.")
        print("Your own traces are the only receipt. Run: ledger.py my-runs.json")
        print("=" * 78)
    elif a.runs:
        path = a.runs
    else:
        p.error("give a runs file, or --example")

    try:
        runs, note = load_runs(path)
    except FileNotFoundError:
        print(f"{path}: no such file", file=sys.stderr)
        return 2
    if not runs:
        print(f"{path}: no runs in this file", file=sys.stderr)
        return 2
    if note:
        print(f"{note}\n")

    try:
        return render(runs, os.path.dirname(os.path.abspath(path)))
    except (ValueError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
