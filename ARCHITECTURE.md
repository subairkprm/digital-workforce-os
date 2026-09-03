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
- role
- permission
- extension
- device
- session
- audit_event

## Environment model
LOCAL -> DEV -> STAGING -> PRODUCTION

Production is not part of DWCO 0.1 implementation.
