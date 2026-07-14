import assert from "node:assert/strict";
import type { AddressInfo } from "node:net";
import { after, before, test } from "node:test";
import { createApp } from "./server";

let baseUrl = "";
let server: ReturnType<ReturnType<typeof createApp>["listen"]>;

before(async () => {
  server = createApp().listen(0);
  await new Promise((resolve) => server.once("listening", resolve));
  baseUrl = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
});

after(async () => {
  await new Promise((resolve) => server.close(resolve));
});

test("GET /invoices returns the open-invoice report as JSON", async () => {
  const res = await fetch(`${baseUrl}/invoices`);

  assert.equal(res.status, 200);
  assert.match(res.headers.get("content-type") ?? "", /application\/json/u);

  const body = (await res.json()) as Array<{ id: string; status: string }>;
  assert.ok(Array.isArray(body));
  assert.ok(body.length > 0);
  assert.ok(body.every((invoice) => invoice.status === "open"));
});

test("GET /invoices rejects an unknown filter", async () => {
  const res = await fetch(`${baseUrl}/invoices?filter=bogus`);
  assert.equal(res.status, 400);
});
