import assert from "node:assert/strict";
import { test } from "node:test";
import { InMemoryObjectStore } from "../storage/s3";
import { renderInvoicePdf } from "./render";

const doc = {
  id: "inv_42",
  customer: "Contoso Ltd",
  currency: "USD",
  items: [{ description: "Platform licence", amt: 49900, taxable: true }],
};

test("renderInvoicePdf stores the rendered document", async () => {
  const store = new InMemoryObjectStore("test-bucket", "test-signing-key");
  const key = await renderInvoicePdf(store, doc);

  assert.equal(key, "invoice-inv_42.pdf");
  assert.deepEqual(store.keys(), ["invoice-inv_42.pdf"]);
});

test("the stored document is a PDF", async () => {
  const store = new InMemoryObjectStore("test-bucket", "test-signing-key");
  const key = await renderInvoicePdf(store, doc);
  const body = await store.get(key);

  assert.ok(body);
  assert.equal(body.subarray(0, 5).toString("latin1"), "%PDF-");
  assert.ok(body.includes("INVOICE inv_42"));
});
