# invoicing-api

A small TypeScript invoicing service: invoices, tax totals, PDF export, a payments
webhook, and JWT auth. It compiles, boots, serves, and its tests pass.

**It is synthetic.** It exists to be audited. It contains real bugs that its own
test suite does not catch. Do not read it as an
example of code to copy.

It runs with no database, no API keys, and no accounts: an in-memory store stands
in for Postgres, and an in-memory object store stands in for S3. `npm install`
needs the network once; nothing after that does. Auth is stubbed too: a bearer
JWT is verified with HS256 when one is sent, and an unauthenticated GET falls back
to a read-only demo session so every command below works out of the box.

## Run it

```bash
npm install     # once, needs network
npm test        # tsc + node --test  -> all green
npm run build && npm start   # http://localhost:3000
```

```bash
curl localhost:3000/invoices           # the open-invoice report
curl localhost:3000/invoices/inv_42    # one invoice
curl localhost:3000/invoices/inv_42/total
curl localhost:3000/invoices/inv_42/pdf   # queues a render, returns a signed link
```

## The webhook gate

The payments provider signs each webhook body with HMAC-SHA256 and sends the hex
digest in `X-Signature`. With the server running, post a forged event:

```bash
curl -i -X POST localhost:3000/webhooks/payments -H 'X-Signature: bogus' -d @forged.json
```

Today that returns **HTTP 202**, and `curl localhost:3000/invoices/inv_42` will show
the invoice marked `paid`. It must return **HTTP 401** and leave the invoice
untouched. `node verify_gate.js` runs the same gate against two verify
implementations, offline.
