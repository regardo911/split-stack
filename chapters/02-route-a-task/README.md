# 02 · Route a task

*"Fable 5 thinks. Sonnet 5 builds. One decides. One executes. You don't hire a CEO to write CSS."*

That's the whole roster. `route.py` is that sentence as code: answer three questions about a task, get back the seat it belongs on and the multiple you'd have overpaid by leaving it on the architect.

```bash
python3 route.py --judgment no --mechanical yes --fresh no
python3 route.py --judgment yes
```

A mechanical rename with no fresh fact in it comes back `Haiku 4.5, Fable would bill 10.0x`. Anything with a decision in it comes back `Fable 5, keep on Fable`. Nothing else does.

Now go get the last three tasks you actually ran through a model. Answer the three questions for each. Any of them that ran on Fable and comes back Haiku or Sonnet is money you already left on the floor.

Chapter 10 stops making you ask the questions.
