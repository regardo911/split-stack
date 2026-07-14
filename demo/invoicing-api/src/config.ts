// Service configuration. Every secret comes from the environment; the fallbacks
// are dummy development values so the service starts on a fresh checkout.

export const config = {
  port: Number(process.env.PORT ?? 3000),

  // The payments provider signs each webhook body with this secret.
  webhookSecret: process.env.WEBHOOK_SECRET ?? "whsec_demo",

  // HS256 signing key for the session tokens issued by the auth providers.
  jwtSecret: process.env.JWT_SECRET ?? "jwt_demo_secret",

  // Object storage for rendered invoice PDFs.
  s3Bucket: process.env.S3_BUCKET ?? "invoices-demo",
  s3SigningSecret: process.env.S3_SIGNING_SECRET ?? "s3_demo_signing_key",
  publicBaseUrl: process.env.PUBLIC_BASE_URL ?? "http://localhost:3000",
  signedUrlTtlSeconds: 900,

  dbUrl: process.env.DATABASE_URL ?? "postgres://localhost/invoicing_demo",

  // Development convenience: with no identity provider wired up, unauthenticated
  // GETs fall back to a read-only session so the service is browsable out of the
  // box. Set ALLOW_ANONYMOUS_READS=false to require a token on every request.
  allowAnonymousReads: process.env.ALLOW_ANONYMOUS_READS !== "false",

  defaultCurrency: "USD",
};
