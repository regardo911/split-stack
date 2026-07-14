// Session handling. A request arrives with a bearer JWT; the pipeline verifies
// it, loads the session, and checks it against the revocation list. Every auth
// provider is expected to hand its result to authPipeline() so that those checks
// run exactly once, in one place.

import crypto from "crypto";
import type { NextFunction, Request, Response } from "express";
import { config } from "../config";

export interface Session {
  userId: string;
  scopes: string[];
}

interface Claims {
  sub: string;
  scopes: string[];
  exp: number;
}

const SAFE_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);

/** Sessions revoked before their token expired. Loaded from Redis in production. */
const revoked = new Set<string>();

const ANONYMOUS: Session = { userId: "anonymous", scopes: ["invoices:read"] };

const encode = (value: object): string =>
  Buffer.from(JSON.stringify(value), "utf8").toString("base64url");

const hmac = (data: string, secret: string): string =>
  crypto.createHmac("sha256", secret).update(data).digest("base64url");

/** Issue an HS256 session token. The OAuth and SAML providers call this. */
export function signSessionToken(session: Session, secret: string, ttlSeconds = 3600): string {
  const header = encode({ alg: "HS256", typ: "JWT" });
  const payload = encode({
    sub: session.userId,
    scopes: session.scopes,
    exp: Math.floor(Date.now() / 1000) + ttlSeconds,
  });
  return `${header}.${payload}.${hmac(`${header}.${payload}`, secret)}`;
}

function verifyJwt(token: string, secret: string): Claims | null {
  const parts = token.split(".");
  if (parts.length !== 3) return null;

  const [header, payload, signature] = parts;
  const expected = Buffer.from(hmac(`${header}.${payload}`, secret));
  const actual = Buffer.from(signature);
  if (actual.length !== expected.length) return null;
  if (!crypto.timingSafeEqual(actual, expected)) return null;

  let claims: Claims;
  try {
    claims = JSON.parse(Buffer.from(payload, "base64url").toString("utf8")) as Claims;
  } catch {
    return null;
  }

  if (typeof claims.sub !== "string" || !Array.isArray(claims.scopes)) return null;
  if (typeof claims.exp !== "number" || claims.exp * 1000 <= Date.now()) return null;

  return claims;
}

const bearer = (header: string | undefined): string | undefined => {
  if (!header) return undefined;
  const [scheme, token] = header.split(" ");
  return scheme?.toLowerCase() === "bearer" ? token : header;
};

/**
 * The one path a credential takes to become a session: verify the token, then
 * check the session is still live. Providers under src/auth/ route through here.
 */
export function authPipeline(token: string | undefined): Session | null {
  const raw = bearer(token);
  if (!raw) return null;

  const claims = verifyJwt(raw, config.jwtSecret);
  if (!claims) return null;
  if (revoked.has(claims.sub)) return null;

  return { userId: claims.sub, scopes: claims.scopes };
}

export function authMiddleware(req: Request, res: Response, next: NextFunction) {
  const header = req.header("Authorization");

  if (!header) {
    if (config.allowAnonymousReads && SAFE_METHODS.has(req.method)) {
      (req as Request & { session?: Session }).session = ANONYMOUS;
      return next();
    }
    return res.status(401).end();
  }

  const session = authPipeline(header);
  if (!session) return res.status(401).end();

  (req as Request & { session?: Session }).session = session;
  next();
}
