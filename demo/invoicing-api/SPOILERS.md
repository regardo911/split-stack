# SPOILERS: the seeded bugs

**Stop.** This is the answer key. Run your audit first, then come back and score it.

Every bug below is really in the code, is really reachable at runtime, and is
**not** caught by `npm test` (which passes green with all of them present). Each one
is correct in isolation, and only a cross-file read finds it.

| # | Bug | Where | Severity |
|---|-----|-------|----------|
| 1 | The webhook mutates invoice state before any signature check. `verifySignature` exists in `src/webhooks/verify.ts` and is correct. The handler never calls it. A forged POST marks any invoice paid and gets a 202. | `src/webhooks/payments.ts:26` | P0 |
| 2 | `Math.round` runs on the combined tax **before** it is split across the three jurisdictions, so the per-jurisdiction shares are derived from an already-rounded number. Three-way splits drop or gain a cent. | `src/billing/totals.ts:31` | P1 |
| 3 | N+1: the report loads the invoices in one query, then fires one more query per invoice for its line items. A 200-invoice report costs 201 queries. | `src/db/invoices.ts:33` | P2 |
| 4 | The retry sends no idempotency key. The provider captures a charge that then times out client-side; the retry charges the customer a second time. | `src/jobs/reconcile.ts:11` | P1 |
| 5 | Cross-file: `render.ts` writes the PDF to `invoice-<id>.pdf`, `links.ts` signs a URL for `invoices/<id>/latest.pdf`. Each file is right on its own; together every download 404s. | `src/pdf/render.ts:66` + `src/storage/links.ts:7` | P1 |
| 6 | `samlAssertionToSession` builds a `Session` directly, bypassing `authPipeline`, so revocation and token checks never run for SAML users. `src/auth/oauth/google.ts` shows the pattern it should follow. It looks like the file to copy for a new provider. It is not. | `src/auth/saml/handler.ts:5` | P0 |
| 7 | Naming: billing calls the field `amt`; the rest of the service (`Charge`, the `line_items` table) uses `amountCents` / `amount_cents`. | `src/billing/totals.ts:5` | P3 |

## Reproducing them

```bash
npm run build && npm start

# 1 — forged POST is accepted, invoice flips to paid
curl -X POST localhost:3000/webhooks/payments -H 'X-Signature: bogus' -d @forged.json  # 202
curl localhost:3000/invoices/inv_42                                                     # "status":"paid"

# 2 — inv_44's taxable base is 100017c. Tax comes back 8500; rounding each
#     jurisdiction after its own split gives [4001,3001,1500] = 8502. Two cents gone.
curl localhost:3000/invoices/inv_44/total

# 5 — the signed link 404s, because nothing was ever written to that key
curl -s localhost:3000/invoices/inv_43/pdf     # -> {"download":"http://localhost:3000/files/invoices/inv_43/latest.pdf?..."}
curl -i "<that url>"                           # 404
```

```bash
# 3 — three open invoices, four queries
node -e 'const {db}=require("./dist/db/pool"),{invoiceReport}=require("./dist/db/invoices");
invoiceReport(db,"open").then(r=>console.log(r.length,"invoices,",db.queryCount,"queries"))'

# 4 — one pending charge, two entries on the provider ledger
node -e 'const {StubProvider}=require("./dist/jobs/provider"),{reconcile}=require("./dist/jobs/reconcile");
const p=new StubProvider(new Set(["ch_777"]));
reconcile(p,[{id:"ch_777",amountCents:49900}]).then(()=>console.log(p.ledger))'
```
