// Serves objects out of storage for the signed URLs handed to customers.
// In production the signed URL points straight at S3 and this route does not
// exist; locally it stands in for the bucket's public endpoint.

import { Router } from "express";
import { objectStore } from "../storage/s3";

export const fileRoutes = Router();

fileRoutes.use(async (req, res) => {
  if (req.method !== "GET") return res.status(405).end();

  const key = decodeURIComponent(req.path.replace(/^\//u, ""));
  const body = await objectStore.get(key);
  if (!body) return res.status(404).json({ error: "no such object", key });

  res.type("application/pdf").send(body);
});
