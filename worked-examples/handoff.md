<!-- Illustrative worked example (ch06): the handoff contract that carries the plan to a cheap seat. Not a metered receipt. -->
# Handoff: secure the payments webhook

## Context (read-only — do NOT change these)
- Repo: invoicing-api. Webhook handler: src/webhooks/payments.ts
- Secret: process.env.WEBHOOK_SECRET (already set; never hardcode it)
- Provider signs the raw body with HMAC-SHA256, sends it in header X-Signature

## Task
1. Create src/webhooks/verify.ts exporting verifySignature(rawBody, header, secret)
2. In payments.ts, call it FIRST; on failure return 401 and touch no DB

## Constraints (frozen — violating any of these fails the handoff)
- Edit ONLY src/webhooks/verify.ts and src/webhooks/payments.ts
- Never log the secret or the raw signature
- Compare with crypto.timingSafeEqual, never === (timing attack)

## Verification gate (run these, paste RAW output into Raw results)
| Gate   | Command                                     | Threshold  | Verdict |
|--------|---------------------------------------------|------------|---------|
| unit   | npm test verify.test.ts                     | all pass   |         |
| forged | node demo/invoicing-api/verify_gate.js  | forged 401 |         |

## Escalation triggers (STOP and hand back to the architect if:)
- The provider's scheme isn't HMAC-SHA256 as assumed here
- A gate fails for a reason the task didn't anticipate
- The fix seems to require editing a file not in the allowed list

## Raw results (builder writes; architect never edits)

## Decisions log (architect only)
