// Line-item totals. All money is in integer cents.

export interface LineItem {
  description: string;
  amt: number;
  taxable: boolean;
}

/**
 * Three overlapping jurisdictions tax the same base: state, county, and a city
 * transit levy. Each one is billed as its own line on the tax summary, so the
 * combined rate has to be split back out per jurisdiction.
 */
const TAX_RATES = [0.04, 0.03, 0.015];
const COMBINED_RATE = TAX_RATES.reduce((acc, rate) => acc + rate, 0);

export function subtotal(items: LineItem[]): number {
  return items.reduce((acc, item) => acc + item.amt, 0);
}

/** The taxable base: exempt items (credits, training, shipping) are excluded. */
export function taxableBase(items: LineItem[]): number {
  return subtotal(items.filter((item) => item.taxable));
}

/**
 * Split the tax on `base` across the three jurisdictions, in whole cents.
 * Cents are indivisible, so each share is rounded to the nearest one.
 */
export function taxSplit(base: number): number[] {
  const tax = Math.round(base * COMBINED_RATE);
  return TAX_RATES.map((rate) => Math.round(tax * (rate / COMBINED_RATE)));
}

export function taxTotal(items: LineItem[]): number {
  return taxSplit(taxableBase(items)).reduce((acc, share) => acc + share, 0);
}

export function invoiceTotal(items: LineItem[]): number {
  return subtotal(items) + taxTotal(items);
}
