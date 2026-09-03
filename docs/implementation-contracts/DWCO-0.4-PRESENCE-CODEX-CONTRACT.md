# DWCO 0.4 — Presence contract

## Objective

Add secure workforce presence after tenant identity and directory, without introducing production
realtime infrastructure or expanding into messaging and voice.

## In scope

- Tenant-scoped presence records tied to authenticated users.
- Available, away, busy, and offline states.
- Authenticated self-service presence update and heartbeat endpoints.
- Automatic offline resolution after a 120-second heartbeat expiry.
- Bounded, deterministic tenant directory presence listing under `employee.read`.
- Admin read-only presence view.
- Mobile presence controls, automatic heartbeat, offline-on-sign-out, and directory indicators.
- Alembic migration, cross-tenant, expiry, validation, authorization, and regression tests.

## Security invariants

- Tenant and user identity are always derived from authenticated server context.
- A client can mutate only its own presence within an active tenant membership.
- Directory presence never exposes records outside the resolved tenant.
- Presence listing is bounded to 100 records per request.
- Expired or explicitly offline records always resolve to offline.
- Presence mutations are rate-limited and do not contain credentials or tokens.
- Heartbeats are not administrative audit events and must not become an activity-surveillance log.

## Explicitly deferred

- WebSocket/SSE production transport, push notifications, and presence analytics.
- Messaging, PSTN, WebRTC production calling, eSIM, carrier APIs, billing, AI, Teams, and recording.
- Production deployment, secrets, observability, retention policy, and remote CI bypasses.

## Completion criteria

- Alembic upgrade/downgrade/upgrade through `0004_presence` passes.
- Backend lint, strict typing, tests, coverage, and dependency audit pass.
- Admin typecheck, tests, production build, and dependency audit pass.
- Mobile typecheck, Expo compatibility, and dependency audit pass.
- Docker PostgreSQL/Redis migration and readiness checks pass.
- Cross-tenant and presence-expiry tests pass.
- AGENTS.md completion report is committed.
