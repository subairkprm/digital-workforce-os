# Scope boundaries

## Currently delivered and accepted

- Local platform foundation, tenancy, identity, RBAC, audit, and security controls.
- Admin/security workflows and workforce operations through DWCO 0.3.

## Implemented and merged, pending stage acceptance

- Tenant-scoped presence status, polling, heartbeat expiry, directory visibility, admin read access,
  and mobile controls under `DWCO-0.4-PRESENCE`.
- One-time authenticated realtime connections, live presence events, direct same-tenant messaging,
  durable bounded history, explicit receipts, sender redaction, retention maintenance, a no-op
  provider-neutral notification boundary, and metadata-only administration under DWCO 0.4.

The complete implementation is merged through PR #21, but DWCO 0.4 does not receive stage credit
until the required independent acceptance reviews are recorded.

## Current acceptance boundary

DWCO 0.4 realtime communication is under acceptance review. Review is limited to the merged contract,
implementation, migration, tests, local verification, residual risks, and rollback evidence.

Acceptance does not authorize shared-environment operation or production deployment. The
process-local fan-out implementation must not be represented as production multi-instance realtime.

## Explicitly outside the current boundary

- PSTN, emergency calling, numbering, lawful-intercept obligations, SIP trunks, PBX, or production
  WebRTC calling.
- eSIM issuance, carrier provisioning, or owning a mobile core.
- AI training/inference over communications or automated decisions.
- Billing, payments, taxation, subscription enforcement, or revenue recognition.
- Recording, transcription, surveillance analytics, or employee-performance monitoring.
- Production infrastructure, credentials/data, deployment, migration, or traffic cutover.

## Boundary rules

- External services use provider-neutral adapters and approved data contracts.
- New stored communication types require retention, deletion, export, and tenant-isolation rules.
- Every client channel requires authentication, authorization, rate limits, and abuse analysis.
- Regulatory, privacy, and provider terms are approval inputs, not coding-agent assumptions.
- Scope expansion requires a revised contract and reviewer approval before implementation.
