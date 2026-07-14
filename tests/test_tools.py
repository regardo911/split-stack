"""The arithmetic is correct on READER INPUT.

These tests do not check that a script reprints the book's examples -- that would
only prove a demo still demos. They check that the functions behave on numbers the
reader supplies, and that the ledger refuses to invent an observation it cannot make.

    python3 -m unittest discover -s tests -v

Stdlib only (unittest), like everything else here. No install step, no plugins.
"""

import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(rel):
    """Load a chapter script by path. The scripts are standalone (no package, no
    cross-imports), which is the point -- each one is copy-pasteable on its own."""
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


estimate = load("chapters/03-estimate-a-task/estimate.py")
route_mod = load("chapters/02-route-a-task/route.py")
fallback = load("chapters/09-fallback/fallback.py")
ledger = load("chapters/11-ledger/ledger.py")

REFUSALS = ROOT / "worked-examples" / "refusals"


class TestCost(unittest.TestCase):
    """chapter 3 -- cost(model, tok_in, tok_out, cache_read, batch)"""

    def test_cost_is_rate_times_tokens(self):
        # 15K in on sonnet-5 ($3/M) + 3K out ($15/M) = 0.045 + 0.045
        self.assertAlmostEqual(estimate.cost("sonnet-5", 15_000, 3_000), 0.090)

    def test_cached_reads_bill_at_a_tenth(self):
        # 10K of the 15K input is cached: 5K @ $3/M + 10K @ $0.30/M + 3K @ $15/M
        expected = (5_000 * 3 + 10_000 * 0.3 + 3_000 * 15) / 1e6
        got = estimate.cost("sonnet-5", 15_000, 3_000, cache_read=10_000)
        self.assertAlmostEqual(got, expected)
        # and it is strictly cheaper than paying full rate for the same read
        self.assertLess(got, estimate.cost("sonnet-5", 15_000, 3_000))

    def test_batch_halves_everything(self):
        cold = estimate.cost("fable-5", 150_000, 12_000)
        self.assertAlmostEqual(estimate.cost("fable-5", 150_000, 12_000, batch=True), cold / 2)

    def test_the_levers_compose_on_the_readers_own_numbers(self):
        cached = estimate.cost("opus-4-8", 80_000, 9_000, cache_read=60_000)
        both = estimate.cost("opus-4-8", 80_000, 9_000, cache_read=60_000, batch=True)
        self.assertAlmostEqual(both, cached / 2)

    def test_every_seat_prices_the_same_job_in_rate_order(self):
        seats = ("fable-5", "opus-4-8", "sonnet-5", "haiku-4-5")
        prices = [estimate.cost(m, 40_000, 25_000) for m in seats]
        # architect dearest, typist cheapest -- on the reader's own job
        self.assertEqual(prices, sorted(prices, reverse=True))


class TestRoute(unittest.TestCase):
    """chapter 2 -- route(needs_judgment, mechanical, needs_fresh_fact)"""

    def test_judgment_goes_to_the_architect(self):
        self.assertEqual(route_mod.route(True, False, False), "Fable 5")
        # judgment wins over everything else
        self.assertEqual(route_mod.route(True, True, True), "Fable 5")

    def test_bounded_mechanical_typing_goes_to_the_cheapest_seat(self):
        self.assertEqual(route_mod.route(False, True, False), "Haiku 4.5")

    def test_mechanical_but_needs_a_fresh_fact_leaves_haiku(self):
        # Haiku's knowledge is roughly a year stale -- a fresh fact routes it up.
        self.assertEqual(route_mod.route(False, True, True), "Sonnet 5")

    def test_a_build_defaults_to_the_primary_executor(self):
        self.assertEqual(route_mod.route(False, False, False), "Sonnet 5")

    def test_the_overpay_multiple_is_real_arithmetic(self):
        out = route_mod.OUT
        self.assertEqual(out["Fable 5"] / out["Haiku 4.5"], 10.0)
        self.assertAlmostEqual(out["Fable 5"] / out["Sonnet 5"], 3.333, places=3)

    def test_yesno_parses_what_a_reader_actually_types(self):
        for yes in ("yes", "y", "TRUE", "1"):
            self.assertTrue(route_mod.yesno(yes))
        for no in ("no", "n", "False", "0"):
            self.assertFalse(route_mod.yesno(no))


class TestFallback(unittest.TestCase):
    """chapter 9 -- served_by_fallback() and classify_refusal()"""

    def test_served_by_fallback_on_a_fallback_shaped_response(self):
        receipt = json.loads((REFUSALS / "fallback_receipt.json").read_text())
        self.assertTrue(fallback.served_by_fallback(receipt))
        model, how = fallback.served_model(receipt)
        self.assertEqual(model, "claude-opus-4-8")
        self.assertIn(".model", how)

    def test_served_by_fallback_on_a_clean_response(self):
        clean = {"model": "claude-fable-5", "stop_reason": "end_turn",
                 "usage": {"iterations": [{"type": "message"}]}}
        self.assertFalse(fallback.served_by_fallback(clean))

    def test_a_refusal_is_not_a_fallback_even_though_a_fallback_ran(self):
        # the fallback was attempted but the request still declined: nobody served it.
        r = {"stop_reason": "refusal",
             "usage": {"iterations": [{"type": "message"}, {"type": "fallback_message"}]}}
        self.assertFalse(fallback.served_by_fallback(r))

    def test_the_cli_envelope_has_no_top_level_model_so_read_modelusage(self):
        # A real `claude -p --output-format json` result: the served model is the
        # highest-costUSD entry in .modelUsage. A housekeeping model also appears.
        envelope = {
            "type": "result", "subtype": "success", "total_cost_usd": 0.42,
            "modelUsage": {
                "claude-haiku-4-5": {"costUSD": 0.002},
                "claude-opus-4-8": {"costUSD": 0.418},
            },
        }
        self.assertNotIn("model", envelope)
        model, how = fallback.served_model(envelope)
        self.assertEqual(model, "claude-opus-4-8")
        self.assertIn("modelUsage", how)

    def test_classify_refusal_routes_each_of_the_five_categories(self):
        for category in ("cyber", "bio", "frontier_llm", "reasoning_extraction", None):
            with self.subTest(category=category):
                name = category if category else "null"
                fixture = REFUSALS / f"refusal_{name}.json"
                got = fallback.classify_refusal(json.loads(fixture.read_text()))
                self.assertEqual(got["category"], category)
                self.assertEqual(got["route"], fallback.CATEGORY_PLAYBOOK[category])
                self.assertTrue(got["route"])  # every category is a route, never a dead end

    def test_classify_refusal_returns_none_when_it_is_not_a_refusal(self):
        self.assertIsNone(fallback.classify_refusal({"stop_reason": "end_turn"}))

    def test_it_branches_on_stop_reason_not_on_the_explanation_text(self):
        # stop_details.explanation is display-only prose, not a stable contract.
        # A refusal whose explanation says nothing recognisable still routes.
        r = {"stop_reason": "refusal",
             "stop_details": {"category": "cyber", "explanation": "asdf qwerty",
                              "recommended_model": "claude-opus-4-8",
                              "fallback_credit_token": "fct_9f2a"}}
        got = fallback.classify_refusal(r)
        self.assertEqual(got["category"], "cyber")
        self.assertEqual(got["retry_against"], "claude-opus-4-8")
        self.assertEqual(got["credit_token"], "fct_9f2a")
        # ...and prose that LOOKS like a refusal but isn't one routes nowhere.
        self.assertIsNone(fallback.classify_refusal(
            {"stop_reason": "end_turn", "stop_details": {"explanation": "I refuse, cyber"}}))

    def test_the_meter_tallies_a_stream_a_5xx_dashboard_would_call_green(self):
        fallback.meter.clear()
        for r in [{"stop_reason": "refusal", "usage": {"iterations": [{"type": "message"}]}},
                  {"stop_reason": "end_turn",
                   "usage": {"iterations": [{"type": "message"},
                                            {"type": "fallback_message"}]}}]:
            fallback.record(r)
        self.assertEqual(fallback.meter["total"], 2)
        self.assertEqual(fallback.meter["refused"], 1)
        self.assertEqual(fallback.meter["opus_served"], 1)


class TestLedger(unittest.TestCase):
    """chapter 11 -- reads a real cost, and refuses to invent an observation."""

    def test_it_reads_the_real_cost_off_a_trace(self):
        trace = {"total_cost_usd": 1.86,
                 "modelUsage": {"claude-fable-5": {"costUSD": 1.40},
                                "claude-sonnet-5": {"costUSD": 0.46}}}
        dollars, source = ledger.cost_from_trace(trace)
        self.assertEqual(dollars, 1.86)
        self.assertIn("total_cost_usd", source)   # the documented field, and it says so

    def test_it_sums_modelusage_when_there_is_no_total_and_says_which_it_used(self):
        trace = {"modelUsage": {"claude-fable-5": {"costUSD": 1.40},
                                "claude-sonnet-5": {"costUSD": 0.46}}}
        dollars, source = ledger.cost_from_trace(trace)
        self.assertAlmostEqual(dollars, 1.86)
        self.assertIn("modelUsage", source)

    def test_it_flags_a_trace_whose_two_cost_fields_disagree(self):
        trace = {"total_cost_usd": 1.86,
                 "modelUsage": {"claude-fable-5": {"costUSD": 9.99}}}
        _, source = ledger.cost_from_trace(trace)
        self.assertIn("9.99", source)

    def test_a_hand_entered_cost_is_labelled_as_hand_entered(self):
        dollars, source = ledger.price({"config": "x", "cost_usd": 1.47}, ".")
        self.assertEqual(dollars, 1.47)
        self.assertIn("hand-entered", source)

    def test_it_refuses_to_invent_a_missing_wall_clock_or_bug_field(self):
        run = {"config": "split-stack", "cost_usd": 1.86}   # no observations supplied
        self.assertEqual(ledger.observed(run, "wall_clock_min"), ledger.UNKNOWN)
        self.assertEqual(ledger.observed(run, "cross_file_bug_caught"), ledger.UNKNOWN)
        self.assertIn("observe", ledger.UNKNOWN)

    def test_a_false_bug_flag_is_not_the_same_as_a_missing_one(self):
        # False means "observed, and it shipped the bug". Absent means "you didn't look".
        self.assertIs(ledger.observed({"cross_file_bug_caught": False},
                                      "cross_file_bug_caught"), False)
        self.assertEqual(ledger.observed({}, "cross_file_bug_caught"), ledger.UNKNOWN)

    def test_it_will_not_price_a_run_with_no_trace_and_no_cost(self):
        with self.assertRaises(ValueError):
            ledger.price({"config": "all-Opus"}, ".")

    def test_end_to_end_on_a_readers_own_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "split.json"), "w") as f:
                json.dump({"total_cost_usd": 2.01,
                           "modelUsage": {"claude-sonnet-5": {"costUSD": 2.01}}}, f)
            runs = [
                {"config": "split-stack", "trace": "split.json",
                 "wall_clock_min": 12, "cross_file_bug_caught": True},
                {"config": "all-Opus", "cost_usd": 1.10, "cross_file_bug_caught": False},
            ]
            runs_file = os.path.join(tmp, "runs.json")
            with open(runs_file, "w") as f:
                json.dump(runs, f)

            loaded, note = ledger.load_runs(runs_file)
            self.assertIsNone(note)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                ledger.render(loaded, tmp)
            out = buf.getvalue()

        self.assertIn("2.01", out)
        self.assertIn("1.10", out)
        self.assertIn("cheapest by cost: all-Opus", out)
        self.assertIn("shipped the cross-file bug: ['all-Opus']", out)
        self.assertIn("unknown", out)        # all-Opus never reported a wall-clock
        self.assertIn("hand-entered", out)   # and its cost was typed in, not metered


if __name__ == "__main__":
    unittest.main()
