#!/usr/bin/env node
// verify_gate.js -- Chapter 6. The webhook verification gate, runnable offline.
//
// The book contracts on the GATE, not the code: any verify implementation is
// acceptable iff a genuine signature passes and a forged one is rejected (401).
// This runs the same gate against two implementations -- a CORRECT constant-time
// HMAC check and a LAZY "trust any signed-looking header" check -- and only one
// clears it. It is educational crypto that runs offline with a dummy secret; it
// is NOT a live surface.
//
//   WEBHOOK_SECRET=whsec_demo node demo/invoicing-api/verify_gate.js
//
// Node built-in `crypto` only. Zero keys, zero network.
"use strict";

const crypto = require("crypto");

// Read-only ground truth. Defaults to the dummy demo secret so the file runs
// standalone; the book sets it inline (WEBHOOK_SECRET=whsec_demo). Never a real secret.
const secret = process.env.WEBHOOK_SECRET || "whsec_demo";
const body = JSON.stringify({ invoice: "inv_42", status: "paid" });
const sign = (b) => crypto.createHmac("sha256", secret).update(b).digest("hex");

const correct = (b, sig) => {                              // one executor writes this
  const a = Buffer.from(sig), e = Buffer.from(sign(b));
  return a.length === e.length && crypto.timingSafeEqual(a, e);  // never ===
};
const lazy = (b, sig) => sig != null;                      // another "helpfully" trusts any header

const good = sign(body);
const forged = good.slice(0, -1) + (good.endsWith("0") ? "1" : "0");
const gate = (v) =>
  (v(body, good) ? "" : "genuine wrongly 401; ") +
  (v(body, forged) ? "GATE FAIL: forged got 202" : "gate holds: forged 401");

console.log("correct verify.ts ->", gate(correct));
console.log("lazy    verify.ts ->", gate(lazy));
