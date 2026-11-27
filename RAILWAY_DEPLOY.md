# ApplyPilot — private Railway deployment

## Deploy
1. Push the contents of this folder to the existing `rajishan2005/ApplyPilot` GitHub repository.
2. In Railway, connect the repository and deploy using `railway.toml`.
3. Add these variables in Railway (never commit actual values):
   - `TAVILY_API_KEY`
   - `GEMINI_API_KEY`
   - `OPENAI_API_KEY`
   - `INVITE_CODE` — the code you give invited testers
   - `ADMIN_DASHBOARD_KEY` — a separate private key used only by you
   - `SESSION_SECRET` — a long random secret (32+ random bytes)
   - `IP_HASH_SECRET` — a separate long random secret; keep it stable to preserve hashed-IP quota history
   - `DAILY_ACTION_LIMIT=3`
   - `SESSION_HOURS=24`
   - `APPLYPILOT_DB_PATH=/data/applypilot.db`
   - `HOST=0.0.0.0`
   - `COOKIE_SECURE=true`
   - `TRUST_PROXY_HEADERS=true`
4. Attach a Railway Volume mounted at `/data` so usage counters and analytics persist across deploys.
5. Generate a Railway public domain. The public homepage displays the invite gate; `/admin` displays the separate owner dashboard login.

## Access controls
- Every application page and API route (except health and auth endpoints) requires a signed, HttpOnly, SameSite=Strict session cookie.
- Invite code is checked server-side using constant-time comparison. Failed attempts are throttled per IP.
- Expensive actions (search, ScamShield scan, Copilot, compare, eligibility) share a rolling quota of 3 per IP per 24 hours. Remaining quota is never exposed to the visitor. On exhaustion, the UI displays a countdown until the oldest action expires.
- Admin analytics require `ADMIN_DASHBOARD_KEY` and a separate signed admin cookie. `/admin` is not linked from the public interface.
- Analytics store HMAC-hashed IP identifiers, not raw IP addresses.

## Important limitations
- An invite code is a shared secret, not individual identity. If a tester shares it, others can use it; rotate `INVITE_CODE` to revoke all existing invite sessions after changing `SESSION_SECRET` if necessary.
- IP limits are not person-level limits. People behind the same campus/office Wi-Fi share one quota; VPNs or mobile networks can change IPs. Use per-user accounts for stronger enforcement.
- The dashboard counts page views and distinct IP hashes, not guaranteed human beings. Automated traffic may be included.
- Keep API keys and admin secrets in Railway Variables only. Do not commit `.env` or the real invite code.
