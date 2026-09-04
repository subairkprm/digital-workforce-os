# Digital Workforce Communication OS

Private, multi-tenant SME workforce communication platform.

## DWCO 0.1 Foundation Scope

This repository begins with:
- multi-tenancy
- authentication
- RBAC
- workforce identity
- audit
- admin shell
- mobile shell
- realtime foundation

External PSTN, eSIM provisioning, AI, recording and advanced PBX are explicitly outside the first implementation contract.

## Phase 1 local development

The Phase 1 monorepo contains:

- `backend/` — FastAPI, SQLAlchemy, Alembic, Redis-backed realtime tickets and security tests
- `admin-web/` — authenticated Next.js administration and messaging-metadata shell
- `mobile/` — Expo/React Native login, directory, presence, direct messaging and secure token storage
- `governance-web/` — read-only project governance and quality control-plane template

Start the local API, PostgreSQL and Redis services:

```bash
cp .env.example .env
docker compose up --build
```

The governance control-plane template is available at `http://localhost:3100`. It is intentionally
isolated from tenant data, GitHub credentials, approvals, merges, and deployment controls. Port 3100
avoids the admin development port (3000) and the API/database/cache ports.

Create the first local tenant owner after the API migration completes:

```bash
docker compose exec api python -m app.bootstrap \
  --tenant-slug demo --tenant-name "Demo Company" \
  --email owner@example.com --password 'choose-a-local-password'
```

The tenant ID returned from the database/bootstrap context is sent as `X-Tenant-ID` on
authenticated tenant API requests. A client-provided tenant ID is never accepted in resource
payloads as authorization context.

DWCO 0.4 adds local direct messaging through authenticated HTTP plus best-effort WebSocket events.
Clients obtain a one-time 60-second connection ticket from `POST /api/v1/realtime/tickets`; access
and refresh tokens are never placed in the WebSocket URL. Durable catch-up uses bounded, ordered
message history. This local implementation is single-process and is not authorized for production.

Run backend quality gates with `make backend-check backend-test`. Migration rollback is
`cd backend && alembic downgrade base`; this is destructive and intended only for disposable local
databases. Production deployment is not authorized by the Phase 1 contract.

## Architecture

- Admin Web: React / Next.js / TypeScript
- Mobile: React Native / TypeScript
- API: FastAPI / Python
- Database: PostgreSQL
- Realtime/cache: Redis
- Voice: WebRTC + coturn in later bounded contract
- Deployment: Docker
- CI: GitHub Actions

See `ARCHITECTURE.md`, `PRODUCT.md`, `IMPLEMENTATION_PLAN.md`, `SECURITY.md`, and `AGENTS.md`.
