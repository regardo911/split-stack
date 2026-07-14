import assert from "node:assert/strict";
import crypto from "node:crypto";
import { test } from "node:test";
import { verifySignature } from "./verify";

const secret = process.env.WEBHOOK_SECRET ?? "whsec_demo";
const body = JSON.stringify({ invoice: "inv_42", status: "paid" });
const good = crypto.createHmac("sha256", secret).update(body).digest("hex");
const forged = good.slice(0, -1) + (good.endsWith("0") ? "1" : "0");

test("verifySignature accepts a genuine signature", () => {
  assert.equal(verifySignature(body, good, secret), true);
});

test("verifySignature rejects a forged signature", () => {
  assert.equal(verifySignature(body, forged, secret), false);
});

test("verifySignature rejects a missing signature", () => {
  assert.equal(verifySignature(body, null, secret), false);
});
