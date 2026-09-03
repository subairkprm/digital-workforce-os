# DWCO 0.3 — Workforce operations contract

## Objective

Deliver secure day-to-day workforce onboarding and lifecycle controls on the existing multi-tenant
foundation without introducing production communications or deployment dependencies.

## In scope

- Tenant-scoped, expiring, single-use user invitations with role assignment.
- Public invitation acceptance using only a high-entropy token; only its digest is stored.
- Invitation listing and revocation for authorized tenant administrators.
- Employee suspend and reactivate transitions with audit events.
- Department manager assignment restricted to an employee in the same tenant.
- Search, status filters, bounded pagination, and deterministic ordering for employee/department APIs.
- Authenticated users can list and revoke their own refresh sessions.
- Admin workflows for invitations, employee lifecycle, search, and department managers.
- Public web invitation-acceptance workflow and tenant-safe invitation-role selection.
- Functional mobile login, secure token persistence, own-profile view, and permitted directory.
- Migration, cross-tenant, token-reuse, authorization, audit, and regression tests.

## Security invariants

- Tenant IDs and actor IDs are always server-derived.
- Invitation tokens are returned once and stored only as SHA-256 digests.
- Invitation acceptance is atomic, expires, and rejects revoked or reused tokens.
- Invitation roles and department managers must belong to the resolved tenant.
- Session endpoints expose and mutate only the authenticated user's sessions.
- Every tenant administrative mutation emits an audit event.
- List limits are capped at 100.

## Explicitly deferred

- Email/SMS delivery and production password-reset delivery adapters.
- PSTN, WebRTC production calling, eSIM, carrier APIs, billing, AI, Teams, and recording.
- Production deployment, production secrets, and remote CI bypasses.

## Completion criteria

- Alembic upgrade/downgrade/upgrade passes.
- Backend lint, typing, tests, coverage, and dependency audit pass.
- Admin typecheck, tests, and production build pass.
- Mobile checks pass.
- Docker PostgreSQL/Redis migration and readiness checks pass.
- AGENTS.md completion report is committed.
