<!-- Illustrative worked example (ch08): a graded verdict with no Blocker or Major, so it SHIPs. Not a metered receipt. -->
VERDICT: SHIP

- MINOR    src/billing/totals.ts:52 — a comment says "cents" but the variable is
  dollars; harmless today, confusing later. Fix in passing if you're in the file.
- NIT      src/webhooks/verify.ts:3 — `sig` could be named `signatureHeader`.

No Blocker, no Major. Note the minor and the nit, then ship.
