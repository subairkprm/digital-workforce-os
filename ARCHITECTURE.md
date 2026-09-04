# Architecture Baseline

## Principles
- Tenant-first
- Provider-neutral
- API-first
- Event-driven
- Mobile-first
- Security-by-default
- No production mutation from coding agents

## Logical architecture

```text
Clients
  |
Edge/WAF
  |
API Gateway
  +-- Auth / Identity
  +-- Tenant Resolver
  +-- Workforce
  +-- Messaging
  +-- Realtime
  +-- Voice (later contract)
  +-- Mobility (later contract)
  +-- Integrations
  +-- AI (later contract)
  |
PostgreSQL + Redis + Object Storage
```

## Tenant boundary
Every tenant-owned business record must include `tenant_id`.
Tenant identity must be derived from authenticated server-side context, never trusted from arbitrary client input.

## Core entities
- tenant
- user
- membership
- employee
- department
- presence
- conversation
- conversation_participant
- message
- message_receipt
- role
- permission
- extension
- device
- session
- audit_event

## Realtime and messaging boundary

- Authenticated HTTP owns durable commands, ordered history, idempotency, receipts, redaction, and
  retention maintenance.
- WebSocket carries best-effort live events after a one-time Redis ticket is consumed and active
  tenant membership is revalidated.
- PostgreSQL is the message authority. A missed live event is recovered with sequence-based history;
  WebSocket delivery is not claimed to be exactly once.
- The local fan-out hub is process-local. A reviewed shared-broker adapter and deployment contract
  are required before multi-instance or production operation.
- The notification adapter receives identifiers only. The current local adapter sends nothing and
  stores no provider credentials.

## Environment model
LOCAL -> DEV -> STAGING -> PRODUCTION

Production is not part of DWCO 0.1 implementation.
