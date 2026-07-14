// Entry point. Untrusted input enters at the webhook body, the POST route
// bodies, and the ?filter= query string on GET /invoices.

import express from "express";
import { config } from "./config";
import { authMiddleware } from "./auth/mw";
import { invoiceRoutes } from "./routes/invoices";
import { fileRoutes } from "./routes/files";
import { paymentsWebhook } from "./webhooks/payments";

export function createApp() {
  const app = express();

  // The provider signs the bytes it sent, so the webhook needs the body exactly
  // as delivered — before any parser gets to rewrite it, and whatever
  // content-type the delivery declares.
  app.post("/webhooks/payments", express.raw({ type: "*/*" }), paymentsWebhook);

  app.use(express.json());

  app.get("/health", (_req, res) => {
    res.json({ ok: true });
  });

  // Object downloads carry their own expiring signature in the query string.
  app.use("/files", fileRoutes);

  app.use(authMiddleware);
  app.use("/invoices", invoiceRoutes);

  return app;
}

if (require.main === module) {
  createApp().listen(config.port, () => {
    console.log(`invoicing-api listening on http://localhost:${config.port}`);
  });
}
