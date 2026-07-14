// Invoice routes. The ?filter= query is untrusted input.

import { Router } from "express";
import { db } from "../db/pool";
import { getInvoice, getLineItems, invoiceReport } from "../db/invoices";
import { invoiceTotal, subtotal, taxTotal } from "../billing/totals";
import { jobQueue } from "../jobs/queue";
import { renderInvoicePdf } from "../pdf/render";
import { objectStore } from "../storage/s3";
import { downloadUrl } from "../storage/links";

const STATUSES = new Set(["open", "paid", "void"]);

export const invoiceRoutes = Router();

invoiceRoutes.get("/", async (req, res) => {
  const filter = String(req.query.filter ?? "open");
  if (!STATUSES.has(filter)) return res.status(400).json({ error: "unknown filter" });

  res.json(await invoiceReport(db, filter));
});

invoiceRoutes.get("/:id", async (req, res) => {
  const invoice = await getInvoice(db, req.params.id);
  if (!invoice) return res.status(404).end();

  res.json(invoice);
});

invoiceRoutes.get("/:id/total", async (req, res) => {
  const invoice = await getInvoice(db, req.params.id);
  if (!invoice) return res.status(404).end();

  const items = await getLineItems(db, invoice.id);
  res.json({
    id: invoice.id,
    currency: invoice.currency,
    subtotal: subtotal(items),
    tax: taxTotal(items),
    total: invoiceTotal(items),
  });
});

// The download link for the invoice PDF. Rendering happens on the job queue, so
// the link is handed back immediately and the file lands a moment later.
invoiceRoutes.get("/:id/pdf", async (req, res) => {
  const invoice = await getInvoice(db, req.params.id);
  if (!invoice) return res.status(404).end();

  const items = await getLineItems(db, invoice.id);
  jobQueue.enqueue(() =>
    renderInvoicePdf(objectStore, {
      id: invoice.id,
      customer: invoice.customer,
      currency: invoice.currency,
      items,
    }).then(() => undefined),
  );

  res.status(202).json({ id: invoice.id, download: downloadUrl(objectStore, invoice.id) });
});
