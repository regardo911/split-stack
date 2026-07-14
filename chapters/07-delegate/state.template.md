<!--
state.template.md. Chapter 7, Appendix A5. The run's file-based memory, so any
seat can resume from it after a stop, an inspection, or a fresh executor picking
it up cold. This is Chapter 6's rule (only what lives in a file counts), applied
to a run in motion. When the transcript compacts or you /clear, this file is the
memory that survives.
-->

# state.md: the run's memory, so any seat can resume from it
- Step 1 verify helper: DONE, gate: tests green
- Step 2 handler change: DONE, gate: webhook replay returns 200
- Step 3 retry-vs-alert policy: ESCALATED to Fable, awaiting decision
- Escalations so far: Step 3 to Fable (judgment), logged
- Remaining: write the decision back, re-run the gate, ship
- Cost so far: $0.09 on Sonnet
