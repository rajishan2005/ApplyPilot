# ApplyPilot

**Discover smarter. Verify before you apply.**

ApplyPilot helps students discover hackathons, internships and scholarships, compare opportunities, inspect trust signals, check eligibility and prepare application drafts.

## Private preview features

- Invite-code gate before the app and its APIs can be used.
- Signed, HttpOnly, SameSite=Strict session cookies.
- Separate owner dashboard at `/admin`, protected by its own key.
- Privacy-preserving analytics: page views, distinct IP visitors, usage actions and quota blocks. IPs are stored as keyed hashes, not raw addresses.
- Three costly actions per IP in a rolling 24-hour window. Search, ScamShield scan, Copilot, comparison and eligibility checks share this limit. Remaining quota is not shown; after the limit is reached, the interface displays a countdown until access returns.
- Failed invite/admin attempts are throttled per IP.
- Opportunity discovery, evidence-oriented ScamShield, eligibility analysis, comparison and application-draft workflow.

## Local setup

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Windows PowerShell: Copy-Item .env.example .env
python server.py
```

Open `http://localhost:8765`. For local HTTP testing, set `COOKIE_SECURE=false` in `.env`. Set a long random `SESSION_SECRET`, a private `INVITE_CODE`, and a different `ADMIN_DASHBOARD_KEY` before starting.

## Railway deployment

See [`RAILWAY_DEPLOY.md`](./RAILWAY_DEPLOY.md). In short:

1. Deploy this repository on Railway.
2. Add Tavily, Gemini and OpenAI API keys as Railway Variables.
3. Add `INVITE_CODE`, `ADMIN_DASHBOARD_KEY`, and a random `SESSION_SECRET` and a separate stable `IP_HASH_SECRET` (each at least 32 random bytes).
4. Set `DAILY_ACTION_LIMIT=3`, `SESSION_HOURS=24`, `COOKIE_SECURE=true`, and `TRUST_PROXY_HEADERS=true`.
5. Attach a Railway Volume mounted at `/data` and set `APPLYPILOT_DB_PATH=/data/applypilot.db`.
6. Generate a public domain. Share the URL and invite code only with selected testers.

### Environment variables

| Variable | Purpose |
|---|---|
| `TAVILY_API_KEY` | Live web discovery and extraction |
| `GEMINI_API_KEY` | Opportunity extraction and AI analysis |
| `OPENAI_API_KEY` | Eligibility, comparison and Copilot |
| `INVITE_CODE` | Shared code required to enter the app |
| `ADMIN_DASHBOARD_KEY` | Separate owner-only dashboard password |
| `SESSION_SECRET` | Signs invite and admin session cookies; keep private |
| `IP_HASH_SECRET` | Stable secret used to hash IPs for quota and analytics |
| `DAILY_ACTION_LIMIT` | Shared per-IP rolling daily limit; default 3 |
| `SESSION_HOURS` | Session cookie lifetime; default 24 hours |
| `APPLYPILOT_DB_PATH` | SQLite database path; use `/data/applypilot.db` on Railway |
| `COOKIE_SECURE` | Set `true` on HTTPS deployments; `false` only for local HTTP |
| `TRUST_PROXY_HEADERS` | Trust Railway's forwarded client IP header |

## Owner dashboard

Open `https://YOUR-RAILWAY-DOMAIN/admin` and enter `ADMIN_DASHBOARD_KEY`. It shows 24-hour page views, unique IP visitors, costly actions, quota blocks, a seven-day activity chart and recent events. The dashboard is not linked from the public app.

## Usage-limit behavior

The quota is **three combined AI/search actions per IP per rolling 24 hours**, not three searches plus three scans. A search, ScamShield scan, Copilot question, comparison or eligibility check consumes one action. Failed provider attempts also consume an action because they may still incur provider costs. After three actions, the server returns a reset timestamp and the frontend displays a countdown. The visitor is not told how many actions remain.

## Security and privacy notes

- Never commit `.env`, API keys, invite codes, admin keys, session secrets or the SQLite database.
- The invite code is shared among invitees, not a unique per-person account. Anyone who receives it can share it. Rotate it if it leaks.
- Per-IP limits are not per-person identity: users on the same campus Wi-Fi share a quota, and VPN/mobile-network changes can change an IP.
- Analytics use keyed IP hashes, not raw IP addresses. Counts are approximate unique IPs, not guaranteed unique humans.
- This prototype's student profile, shortlist and application records are still stored in a shared workspace. Tell testers to use demo information only; do not enter sensitive personal data.
- ScamShield provides risk indicators and evidence leads, not a guarantee or legal fraud determination.
- For a larger public launch, add individual accounts, per-user data isolation, stronger edge rate limiting and a managed database.

## Tests

```bash
python -m unittest discover -s tests -v
node --check static/app.js
```
