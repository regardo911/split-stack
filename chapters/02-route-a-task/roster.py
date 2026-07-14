#!/usr/bin/env python3
# roster.py -- the receipt behind the table's last column.
# rate = ($ per million input tokens, $ per million output tokens), launch pricing.
RATE = {
    "Fable 5":   (10, 50),   # architect -- judgment only
    "Opus 4.8":  (5, 25),    # heavy specialist / Fable's fallback target
    "Sonnet 5":  (3, 15),    # primary executor -- your default typist
    "Haiku 4.5": (1, 5),     # cheap typist -- bounded mechanical work
}
fable_out = RATE["Fable 5"][1]

# The only column your budget feels: output cost relative to the architect.
for seat, (r_in, r_out) in RATE.items():
    print(f"{seat:10} ${r_in}/${r_out} per MTok   {r_out / fable_out:.1f}x Fable out")

# The receipt: price ONE fixed 50K-output-token job on every seat.
print()
job = 50_000
for seat, (_, r_out) in RATE.items():
    print(f"{seat:10} 50K-token job   ${job / 1_000_000 * r_out:.2f}")

print(f"\nsame keystrokes, {RATE['Fable 5'][1] / RATE['Haiku 4.5'][1]:.0f}x apart: architect vs typist")
