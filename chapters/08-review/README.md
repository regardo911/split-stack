# 08 · Review, once

The cheap seat just wrote your code. Before it ships, someone senior should read it, and the seat that wrote the diff is the least likely to catch its own deep mistakes, because it made them from inside its own limited view.

So you buy a little frontier budget back. One pass. Four severities. A verdict.

First, decide whether the diff even earns a senior:

```bash
git diff --name-only main > changed.txt
bash needs-senior.sh changed.txt
```

Money, auth, crypto, anything crossing files: that earns the expensive seat, because that's where the expensive-to-ship bug hides. A rename ships on its gate. Reviewing a trivial diff with Fable is the same mistake as typing with it.

Then grade it, and let the rule make the call:

```bash
git diff main > change.diff
claude --model fable --effort high "$(cat review-rubric.md)
$(cat change.diff)" > verdict.md

bash gate.sh verdict.md
```

```
blocker=1 major=0 minor=1 nit=1
DECISION: SEND BACK
```

The gate never deliberates. The judgment already happened in the review, so collapsing it to a decision is arithmetic. One blocker sends the diff back no matter how clean the rest of it is. A verdict carrying only nits ships, untouched.

## Now the part where you stop

The obvious next thought is: why am *I* in the middle? Why not wire it so Fable reviews, the executor auto-fixes, Fable reviews again, and it loops until the verdict is SHIP?

Don't build that from here. When does it stop, if the judge keeps finding one more nit? How do you keep two models ping-ponging politely forever while the meter runs? Every iteration is another full pass on the most expensive seat, which is the fifty-dollar runaway from Chapter 7 wearing a reviewer's suit.

**You are the exit condition.** You're the thing that stops at "good enough" instead of "perfect and bankrupt." Keep the human in the seam.

One more thing worth knowing: Fable is a fallible reviewer. It will occasionally flag a Blocker that's fine on a closer look. Go to the `file:line` and read the code before you route a fix. A review you've stopped reading is a review that's always right.
