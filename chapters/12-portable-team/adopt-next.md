<!--
adopt-next.md. Chapter 12. The next-flagship adoption routine. When a new model
ships, don't trust its launch benchmarks. Measure it on YOUR work. This whole
file is the routine; it survives you like every other artifact because it's a
committed file, not a habit. Fold it into your portable model-team repo.
-->

# adopt-next.md: the next-flagship adoption routine
1. Seat it:  swap the new model into the architect seat (the swap drill).
2. Meter it: run the Chapter 11 three-way ledger on one representative task.
3. Curve it: measure its effort curve on your tasks; folk equivalences never transfer.
4. Update the roster card with its real cost and its real judgment quality.
5. Keep it only if the receipt says so; otherwise keep the old seat.

<!--
The swap drill itself (Chapter 12). Prove nothing breaks when the model changes:
  claude --version                 # aliases still resolve? want a version line, not an error
  claude --model best              # `best` = Fable where entitled, else latest Opus
  export ANTHROPIC_DEFAULT_FABLE_MODEL="<the-profile-your-org-allows>"
  claude --model fable
Then run /architect on a real task and confirm the same route, different seat.

Do one subtraction while you're at it: strip the workarounds. Prompts written for
a prior model are often too prescriptive for the next tier and reduce its output
quality. Prune before you tune.
-->
