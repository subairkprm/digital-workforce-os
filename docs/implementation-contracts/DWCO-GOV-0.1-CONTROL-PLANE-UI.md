# DWCO-GOV 0.1 — Governance control-plane UI contract

CONTRACT_STATUS=APPROVED_BY_USER_FOR_BOUNDED_LOCAL_IMPLEMENTATION

## Objective

Provide an isolated, read-only dashboard template for project plan, stage, PR quality, acceptance,
checkpoint, requirement, and deviation visibility without changing customer workflows or granting
repository or production control.

## In scope

- Static responsive governance dashboard at local port 3100.
- Separate accepted, implemented, and readiness measures.
- Stage, PR evidence, reviewer, deviation, and journey views.
- Docker Compose integration as an isolated unprivileged read-only service.
- Representative evidence from the current DWCO 0.4 checkpoint.
- Version-controlled project plan and Mermaid architecture, evidence, record, and gate diagrams.

## Security boundaries

- No database, Redis, API, GitHub, secret, or production connection.
- No authentication claim; this is a local UI template only.
- No merge, approval, waiver, deployment, or stage-status mutations.
- No customer, employee, message, credential, or production data.
- Any future live integration requires authentication, RBAC, audit, signed webhook/API ingestion,
  data minimisation, and a separate approved contract.

## Explicitly deferred

- Persistent governance records, live GitHub synchronization, webhooks, and status checks.
- Reviewer identity/signature workflows and immutable approvals.
- Customer or production deployment.

## Acceptance criteria

- Existing API, PostgreSQL, Redis, and admin development ports do not conflict.
- Compose configuration validates and the governance image builds.
- The service starts read-only and returns HTTP 200 at port 3100.
- UI works at desktop and narrow layouts and exposes no mutating controls.
- Existing application behavior remains unchanged.

DEPLOYMENT_STATUL=LOCAL_ONLY_NOT_AUTHORIZED_FOR_PRODUCTION
