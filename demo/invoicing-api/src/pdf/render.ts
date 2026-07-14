// Invoice PDF rendering. Called off the request path by the job queue.

import type { ObjectStore } from "../storage/s3";
import type { LineItem } from "../billing/totals";
import { invoiceTotal, subtotal, taxTotal } from "../billing/totals";

export interface InvoiceDoc {
  id: string;
  customer: string;
  currency: string;
  items: LineItem[];
}

const money = (cents: number): string => (cents / 100).toFixed(2);

/** Escape the characters that would otherwise break a PDF string literal. */
const pdfEscape = (text: string): string => text.replace(/([\\()])/gu, "\\$1");

function invoiceLines(doc: InvoiceDoc): string[] {
  const lines = [`INVOICE ${doc.id}`, doc.customer, ""];
  for (const item of doc.items) {
    lines.push(`${item.description}   ${doc.currency} ${money(item.amt)}`);
  }
  lines.push("");
  lines.push(`Subtotal   ${doc.currency} ${money(subtotal(doc.items))}`);
  lines.push(`Tax        ${doc.currency} ${money(taxTotal(doc.items))}`);
  lines.push(`Total      ${doc.currency} ${money(invoiceTotal(doc.items))}`);
  return lines;
}

/** A single-page PDF 1.4 document. The real service hands this to the layout engine. */
export function renderPdfBytes(doc: InvoiceDoc): Buffer {
  const text = invoiceLines(doc)
    .map((line, index) => `${index === 0 ? "" : "T*\n"}(${pdfEscape(line)}) Tj`)
    .join("\n");

  const content = `BT\n/F1 12 Tf\n14 TL\n56 760 Td\n${text}\nET\n`;

  const objects = [
    "<< /Type /Catalog /Pages 2 0 R >>",
    "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
    "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
    `<< /Length ${Buffer.byteLength(content, "latin1")} >>\nstream\n${content}\nendstream`,
    "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
  ];

  let pdf = "%PDF-1.4\n";
  const offsets: number[] = [];
  objects.forEach((body, index) => {
    offsets.push(Buffer.byteLength(pdf, "latin1"));
    pdf += `${index + 1} 0 obj\n${body}\nendobj\n`;
  });

  const xrefOffset = Buffer.byteLength(pdf, "latin1");
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  for (const offset of offsets) {
    pdf += `${String(offset).padStart(10, "0")} 00000 n \n`;
  }
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF\n`;

  return Buffer.from(pdf, "latin1");
}

/** Render the invoice and store it. Returns the key the PDF was written to. */
export async function renderInvoicePdf(store: ObjectStore, doc: InvoiceDoc): Promise<string> {
  const key = `invoice-${doc.id}.pdf`;
  await store.put(key, renderPdfBytes(doc));
  return key;
}
