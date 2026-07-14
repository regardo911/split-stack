<!-- Illustrative worked example (ch04): a Fable audit of the demo invoicing-api. Not a metered receipt. -->
# Audit — invoicing-api (analysis only, no edits)

## Phase 1 — Discovery
- Entry points: src/server.ts (Express app), 14 routes under src/routes/
- Data flow: request → route → service (src/billing, src/invoices)
  → db layer (src/db, Postgres) → response; PDFs rendered async in
  src/pdf/render.ts via a job queue
- External boundaries:
  - Payments webhook: POST /webhooks/payments  (untrusted, public)
  - Auth: JWT in Authorization header, verified in src/auth/mw.ts
  - Third-party: payment provider API, S3 for PDF storage
- Untrusted input enters at: the webhook body, all POST route bodies,
  and the `?filter=` query string on GET /invoices

## Phase 2 — Audit

### Webhook signature never verified
- WHAT: the handler mutates invoice state before checking the provider signature.
- WHERE: src/webhooks/payments.ts:41
- WHY: Anyone who knows the endpoint URL can mark any invoice "paid" with a forged POST.
- SEVERITY: P0

### Tax split rounds before applying the split
- WHAT: Math.round runs on the pre-split total instead of after the split.
- WHERE: src/billing/totals.ts:118
- WHY: three-way tax splits drop or gain a cent per line item. Wrong money on real invoices.
- SEVERITY: P1

### Reconciliation retries a charge with no idempotency key
- WHAT: a slow-but-successful charge is retried on a network timeout and charged twice.
- WHERE: src/jobs/reconcile.ts:88
- WHY: customers get intermittently double-charged; needs whole-system reasoning to see.
- SEVERITY: P1

### N+1 query loading line items
- WHAT: each invoice refetches its line items in a loop.
- WHERE: src/db/invoices.ts:76
- WHY: a 200-invoice report fires 201 queries. Slow now, a timeout at scale.
- SEVERITY: P2

### PDF download key mismatch across files
- WHAT: render.ts writes one S3 key; links.ts signs a different one.
- WHERE: src/pdf/render.ts + src/storage/links.ts
- WHY: every generated PDF 404s on download; correct in isolation, broken in composition.
- SEVERITY: P2

### Inconsistent money-field name
- WHAT: `amt` is used where the rest of billing uses `amountCents`.
- WHERE: src/billing/totals.ts
- WHY: readability only, no behavior impact; a mechanical rename.
- SEVERITY: P3

## Phase 3 — Improvement strategy
- Input validation: verify the webhook signature before any mutation; reject unsigned.
- Money correctness: round after the split; give reconcile an idempotency key.
- Performance: batch line-item loading with a join.
- Consistency: unify the S3 key format; rename the stray money field.

## Phase 4 — Task plan
| Task | Size | Milestone | Owner model |
|------|------|-----------|-------------|
| Verify webhook signature before processing        | M | M0 | Opus 4.8 (security judgment) |
| Move Math.round to after the tax split            | S | M0 | Sonnet 5 (specified fix) |
| Add an idempotency key to the reconcile retry     | M | M0 | Fable 5 (judgment: correctness policy) |
| Batch line-item loading with a join               | M | M1 | Sonnet 5 |
| Unify the PDF S3 key across render + links         | M | M1 | Fable 5 (cross-file judgment) |
| Rename `amt` → `amountCents` across billing        | S | M2 | Haiku 4.5 (mechanical) |
