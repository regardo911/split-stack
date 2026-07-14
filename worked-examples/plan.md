<!-- Illustrative worked example (ch05): the webhook plan, five fields per step. Not a metered receipt. -->
# Plan: secure the payments webhook

## Step 1 — Add signature verification helper
- Goal: a reusable function that verifies the provider's webhook signature.
- Files touched: src/webhooks/verify.ts (new), src/config.ts (read WEBHOOK_SECRET)
- Change: export verifySignature(rawBody, header, secret) using HMAC-SHA256,
  constant-time compare, returns boolean. No side effects, no logging.
- Owner model: Sonnet 5
- Done when: unit test verify.test.ts passes for a known-good and known-bad sig.

## Step 2 — Enforce verification in the handler
- Goal: reject unverified webhook requests before any invoice mutation.
- Files touched: src/webhooks/payments.ts
- Change: call verifySignature on the raw body FIRST; on false, return 401 and
  do not touch the DB. Move the existing body-parse below the check.
- Owner model: Sonnet 5
- Done when: a forged POST returns 401; a valid POST still updates invoice status.

## Step 3 — Decide retry + logging policy for rejected webhooks
- Goal: choose how the system responds to repeated bad signatures.
- Files touched: src/webhooks/payments.ts, docs/security.md
- Change: JUDGMENT — is a bad sig an attack (alert) or a config drift (retry)?
  Decide the policy, then encode it.
- Owner model: Fable 5 (escalate — this is a policy decision, not typing)
- Done when: security.md states the policy and the handler implements it.
