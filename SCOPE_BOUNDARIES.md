# Scope boundaries

## Currently delivered and accepted

- Local platform foundation, tenancy, identity, RBAC, audit, and security controls.
- Admin/security workflows and workforce operations through DWCO 0.3.

## Delivered and accepted through DWCO 0.4

- Tenant-scoped presence status, polling, heartbeat expiry, directory visibility, admin read access,
  and mobile controls under `DWCO-0.4-PRESENCE`.
- One-time authenticated realtime connections, live presence events, direct same-tenant messaging,
  durable bounded history, explicit receipts, sender redaction, retention maintenance, a no-op
  provider-neutral notification boundary, and metadata-only administration under DWCO 0.4.

The complete implementation and acceptance remediation are merged through `607e6c0`; PR #25 records
the accepted status on `main` at `9188adc`. Required reviews are recorded and DWCO 0.4 contributes
its accepted 14 percentage points. External CI and deployment exceptions remain open.

## Current approval boundary

DWCO 0.5 app-to-app voice/WebRTC is in contract review only. Implementation remains unauthorized until
the separate contract gate passes; contract review does not add product completion weight.

Acceptance does not authorize shared-environment operation or production deployment. The
existing process-local fan-out implementation must not be represented as production multi-instance
realtime.

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
