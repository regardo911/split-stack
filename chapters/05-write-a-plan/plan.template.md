<!--
plan.template.md. Chapter 5, Appendix A2. Fable writes this from the audit.
The highest-return file you'll build: five fields per step, ordered so nothing
depends on a later step, each step pre-routed to the cheapest seat that can
execute it as written.

Quality bar: a cheap seat must be able to execute any single step with zero
additional judgment. Test it with `claude --model sonnet` on the step you trust
least; if it asks a question, that answer is a judgment your plan is missing.

This is a TEMPLATE. A worked instance ships at ../../worked-examples/plan.md. Read the
routing table straight off any filled plan:
    grep -E '^- Owner model:' ../../worked-examples/plan.md | sort | uniq -c
-->

# Plan: <goal>

## Step N — <title>
- Goal: what this step accomplishes, one sentence.
- Files touched: every file this step reads or edits, listed explicitly.
- Change: the specific edit, concrete enough that nothing is left to decide.
- Owner model: the cheapest seat that can execute the change as written.
- Done when: the observable condition that proves the step worked.

<!--
Field notes:
- Files touched is the whole trick: it hands the executor the scope as a fact so
  it doesn't crawl the repo re-deriving your architecture, and it is a tripwire:
  a step that edits a file not on its list has quietly sprawled.
- Ordering is judgment: lay steps down so nothing references anything a later
  step creates. A good plan reads like a build.
- Owner model turns the plan into a routing table. Most steps are Sonnet;
  mechanical steps drop to Haiku; a step where judgment recurs escalates to Fable.
- "Done when" is a bar, not an adjective. "The forged POST returns 401", never
  "the webhook is secure".
-->
