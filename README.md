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

- `backend/` — FastAPI, SQLAlchemy, Alembic, Redis readiness and security tests
- `admin-web/` — authenticated Next.js administration shell
- `mobile/` — Expo/React Native login, profile/directory shell and secure token storage

Start the local API, PostgreSQL and Redis services:

```bash
cp .env.example .env
docker compose up --build
```

Create the first local tenant owner after the API migration completes:

```bash
docker compose exec api python -m app.bootstrap \
  --tenant-slug demo --tenant-name "Demo Company" \
  --email owner@example.com --password 'choose-a-local-password'
```

The tenant ID returned from the database/bootstrap context is sent as `X-Tenant-ID` on
authenticated tenant API requests. A client-provided tenant ID is never accepted in resource
payloads as authorization context.

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
