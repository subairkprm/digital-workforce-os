# Scope boundaries

## Currently delivered and accepted

- Local platform foundation, tenancy, identity, RBAC, audit, and security controls.
- Admin/security workflows and workforce operations through DWCO 0.3.

## Implemented prerequisite, not full-stage acceptance

- Tenant-scoped presence status, polling, heartbeat expiry, directory visibility, admin read access,
  and mobile controls under `DWCO-0.4-PRESENCE`.

## Next proposed boundary

DWCO 0.4 realtime communication may cover secure realtime presence transport and tenant messaging
only after approval of its draft contract. The draft does not itself authorize implementation.

## Explicitly outside the next boundary

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
