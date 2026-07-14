import assert from "node:assert/strict";
import { test } from "node:test";
import { InMemoryObjectStore } from "./s3";
import { downloadUrl } from "./links";

test("downloadUrl signs a time-limited link to the invoice PDF", () => {
  const store = new InMemoryObjectStore("test-bucket", "test-signing-key");
  const url = new URL(downloadUrl(store, "inv_42"));

  assert.equal(url.pathname, "/files/invoices/inv_42/latest.pdf");
  assert.match(url.searchParams.get("signature") ?? "", /^[0-9a-f]{64}$/u);
  assert.ok(Number(url.searchParams.get("expires")) > Date.now() / 1000);
});
