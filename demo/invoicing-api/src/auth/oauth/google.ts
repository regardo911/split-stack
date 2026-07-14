// Google OAuth provider: exchange the authorization code for a token, then hand
// that token to the shared pipeline so the session checks run.

import { authPipeline, type Session } from "../mw";

export function googleOAuthLogin(code: string | undefined): Session | null {
  const token = exchangeCodeForToken(code);
  return authPipeline(token);
}

function exchangeCodeForToken(code: string | undefined): string | undefined {
  // Stand-in for the POST to https://oauth2.googleapis.com/token, which returns
  // an id_token already signed with our own HS256 session key.
  return code;
}
