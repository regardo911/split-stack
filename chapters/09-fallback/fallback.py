#!/usr/bin/env python3
"""fallback.py -- Chapter 9. See the safety wall, and price the switch.

Point it at a REAL run and it tells you which model actually served you.

    claude -p --model fable --output-format json "your task" > run.json
    fallback.py run.json --expect claude-fable-5

It reads both shapes:

  * the Claude Code CLI result envelope -- there is NO top-level `.model` on it.
    The served model comes from `.modelUsage`: the entry that did the real work
    is the highest-`costUSD` one (a small housekeeping model can also appear).
  * a raw API response object -- top-level `model`, and `usage.iterations[]`
    where a `fallback_message` entry is the fingerprint of a silent fallback.

Pass a JSON *list* of responses and it meters them (a refusal is an HTTP 200 --
invisible to every 5xx dashboard you own, so you tally it yourself).

Exits 1 if the served model is not the one you asked for with --expect.

Stdlib only, offline, zero keys. Standalone by design.
"""

import argparse
import json
import sys
from collections import Counter


def served_by_fallback(response):
    """True if a safety fallback quietly served this from another model."""
    iters = (response.get("usage") or {}).get("iterations") or []
    fallback_ran = any(it.get("type") == "fallback_message" for it in iters)
    return fallback_ran and response.get("stop_reason") != "refusal"


CATEGORY_PLAYBOOK = {
    "cyber":                "rephrase, then reroute (benign security work trips this)",
    "bio":                  "rephrase, then reroute (benign life-sciences work trips this)",
    "frontier_llm":         "rephrase if ordinary ML work, else accept (narrow: training infra, kernels)",  # noqa: E501
    "reasoning_extraction": "strip reasoning-echo boilerplate, else accept (never pull the hidden reasoning)",  # noqa: E501
    None:                   "reroute (no named category, so pick a seat on purpose)",
}


def classify_refusal(response):
    """Read a refusal as structured data and return a route.
    Branch on stop_reason; never parse stop_details.explanation."""
    if response.get("stop_reason") != "refusal":
        return None                       # not a refusal, nothing to route
    d = response.get("stop_details") or {}
    category = d.get("category")          # one of the five documented values
    return {
        "category": category,
        "route": CATEGORY_PLAYBOOK.get(category, CATEGORY_PLAYBOOK[None]),
        "retry_against": d.get("recommended_model"),      # set when fallback was skipped
        "credit_token": d.get("fallback_credit_token"),   # echo on a manual Opus retry
    }


meter = Counter()


def record(response):
    """A refusal is an HTTP 200, invisible to 5xx dashboards. Tally it yourself."""
    meter["total"] += 1
    meter["refused"] += response.get("stop_reason") == "refusal"
    meter["opus_served"] += served_by_fallback(response)


# ---------------------------------------------------------------- shape reading

def served_model(response):
    """Which model actually served this? Returns (model, how_we_know).

    The CLI result envelope carries no top-level `.model` -- read `.modelUsage`
    and take the highest-cost entry. A raw API response names it directly.
    """
    usage = response.get("modelUsage")
    if isinstance(usage, dict) and usage:
        top = max(usage.items(), key=lambda kv: (kv[1] or {}).get("costUSD") or 0)
        return top[0], "CLI result envelope: highest-costUSD entry in .modelUsage"
    if response.get("model"):
        return response["model"], "API response: top-level .model"
    return None, "no served model in this object (a refusal before any output names none)"


def report(response, expect):
    """Print who served it, whether a fallback fired, and the route on a refusal."""
    model, how = served_model(response)
    print(f"served by   : {model or 'unknown'}")
    print(f"  read from : {how}")

    iters = (response.get("usage") or {}).get("iterations")
    if iters is not None:
        fired = served_by_fallback(response)
        print(f"fallback    : {'FIRED -- another model quietly served this' if fired else 'no'}")
    elif response.get("modelUsage"):
        print("fallback    : the CLI envelope carries no fallback marker, so the "
              "served-model check above IS the signal")
    else:
        print("fallback    : no usage.iterations[] on this object -- nothing to check")

    refusal = classify_refusal(response)
    if refusal:
        print(f"refusal     : category={refusal['category']!r}")
        print(f"  route     : {refusal['route']}")
        print(f"  retry on  : {refusal['retry_against'] or '(none suggested)'}")
        print(f"  credit    : {refusal['credit_token'] or '(none -- fallback was not skipped)'}")
        print("  (a refusal before any output is not billed at all; what costs you "
              "is what serves it next)")

    if expect:
        if model is None:
            print(f"\nEXPECTED {expect}, but nothing served this request.")
            return 1
        if model != expect:
            print(f"\nWARNING: served by {model}, not {expect} -- "
                  "you paid for one seat's judgment and got another's")
            return 1
        print(f"\nOK: {expect} served this request.")
    return 0


def main():
    p = argparse.ArgumentParser(
        description="Which model actually served your run, and did a fallback fire?",
        epilog="Feed it a real run: claude -p --model fable --output-format json 'task' > run.json",
    )
    p.add_argument("run", help="a JSON run: a CLI result envelope, an API response, or a list")
    p.add_argument("--expect", metavar="MODEL",
                   help="exit 1 unless this model served it, e.g. claude-fable-5")
    a = p.parse_args()

    with open(a.run) as f:
        data = json.load(f)

    if isinstance(data, list):
        meter.clear()
        for i, r in enumerate(data, 1):
            print(f"--- response {i} ---")
            report(r, expect=None)
            record(r)
            print()
        print(f"{meter['total']} calls | {meter['refused']} refused | "
              f"{meter['opus_served']} served by a fallback")
        return 0

    if not isinstance(data, dict):
        print(f"{a.run}: expected a JSON object or a list of them", file=sys.stderr)
        return 2

    return report(data, a.expect)


if __name__ == "__main__":
    raise SystemExit(main())
