// The payments webhook. The provider POSTs here when a charge settles.

import type { Request, Response } from "express";
import { db } from "../db/pool";
import { markPaid } from "../db/invoices";

interface PaymentEvent {
  invoice: string;
  status: string;
}

export async function paymentsWebhook(req: Request, res: Response) {
  const rawBody = req.body as Buffer;

  let event: PaymentEvent;
  try {
    event = JSON.parse(rawBody.toString("utf8")) as PaymentEvent;
  } catch {
    return res.status(400).end();
  }

  if (typeof event.invoice !== "string" || typeof event.status !== "string") {
    return res.status(400).end();
  }

  const updated = await markPaid(db, event.invoice, event.status);
  if (!updated) return res.status(404).end();

  // The provider retries anything that is not a 2xx, so acknowledge fast and let
  // the downstream side effects (receipt email, ledger sync) run off the queue.
  res.status(202).end();
}
