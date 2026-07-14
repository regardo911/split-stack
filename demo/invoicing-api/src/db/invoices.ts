// Invoice data access. Every SQL string in the service lives in this file.

import type { Db, InvoiceRow, LineItemRow, Row } from "./pool";
import type { LineItem } from "../billing/totals";

export async function getInvoice(db: Db, id: string): Promise<InvoiceRow | null> {
  const rows = await db.query("SELECT * FROM invoices WHERE id = $1", [id]);
  return (rows[0] as InvoiceRow | undefined) ?? null;
}

export async function getLineItems(db: Db, invoiceId: string): Promise<LineItem[]> {
  const rows = (await db.query("SELECT * FROM line_items WHERE invoice_id = $1", [
    invoiceId,
  ])) as LineItemRow[];

  return rows.map((row) => ({
    description: row.description,
    amt: Number(row.amount_cents),
    taxable: Boolean(row.taxable),
  }));
}

/**
 * The invoice report: every invoice in a given state, each with its line items
 * attached so the caller can render totals without a second round trip.
 */
export async function invoiceReport(db: Db, filter: string): Promise<Row[]> {
  const invoices = await db.query(
    "SELECT * FROM invoices WHERE status = $1 ORDER BY created_at DESC",
    [filter],
  );

  for (const inv of invoices) {
    inv.lineItems = await db.query("SELECT * FROM line_items WHERE invoice_id = $1", [inv.id]);
  }

  return invoices;
}

export async function markPaid(db: Db, id: string, status: string): Promise<InvoiceRow | null> {
  const rows = await db.query(
    "UPDATE invoices SET status = $1, paid_at = now() WHERE id = $2 RETURNING *",
    [status, id],
  );
  return (rows[0] as InvoiceRow | undefined) ?? null;
}
