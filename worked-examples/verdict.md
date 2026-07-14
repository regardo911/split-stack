<!-- Illustrative worked example (ch08): a graded senior-review verdict that must SEND BACK. Not a metered receipt. -->
VERDICT: SEND BACK

- BLOCKER  src/webhooks/payments.ts:44 — verifySignature is called but its
  return value is ignored; a forged request still proceeds. Fix: `if
  (!verifySignature(...)) return res.status(401).end()`.
- MINOR    src/webhooks/verify.ts:12 — no length check before timingSafeEqual,
  which throws on mismatched buffers. Fix: compare lengths first, return false.
- NIT      src/webhooks/verify.ts:3 — `sig` could be named `signatureHeader`.

Two of three findings are non-blocking. The BLOCKER must be fixed before ship.
