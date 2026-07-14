import assert from "node:assert/strict";
import { test } from "node:test";
import { subtotal, taxableBase, type LineItem } from "./totals";

const items: LineItem[] = [
  { description: "Platform licence", amt: 49900, taxable: true },
  { description: "Overage", amt: 18400, taxable: true },
  { description: "Onboarding credit", amt: -5000, taxable: false },
];

test("subtotal sums every line item in cents", () => {
  assert.equal(subtotal(items), 63300);
});

test("subtotal of an empty invoice is zero", () => {
  assert.equal(subtotal([]), 0);
});

test("the taxable base excludes exempt line items", () => {
  assert.equal(taxableBase(items), 68300);
});
