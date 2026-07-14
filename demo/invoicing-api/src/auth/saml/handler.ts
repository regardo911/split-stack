// SAML provider: turn a signed assertion from the enterprise IdP into a session.

import type { Session } from "../mw";

export function samlAssertionToSession(assertion: string): Session {
  const nameId = parseNameId(assertion);
  const scopes = parseScopes(assertion);
  return { userId: nameId, scopes };
}

function parseNameId(assertion: string): string {
  const match = /<saml:NameID[^>]*>([^<]+)<\/saml:NameID>/u.exec(assertion);
  return match?.[1] ?? "unknown";
}

function parseScopes(assertion: string): string[] {
  const match = /<saml:AttributeValue[^>]*>([^<]+)<\/saml:AttributeValue>/u.exec(assertion);
  return match ? match[1].split(/[,\s]+/u).filter(Boolean) : ["invoices:read"];
}
