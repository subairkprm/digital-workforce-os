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
