// Webhook signature verification.
//
// The payments provider signs the raw request body with HMAC-SHA256 and sends
// the hex digest in the X-Signature header.

import crypto from "crypto";

export function verifySignature(
  rawBody: Buffer | string,
  header: string | null | undefined,
  secret: string,
): boolean {
  if (!header) return false;

  const expected = crypto.createHmac("sha256", secret).update(rawBody).digest("hex");
  const actual = Buffer.from(header);
  const digest = Buffer.from(expected);

  // Length-guard first: timingSafeEqual throws on a length mismatch.
  if (actual.length !== digest.length) return false;

  return crypto.timingSafeEqual(actual, digest);
}
