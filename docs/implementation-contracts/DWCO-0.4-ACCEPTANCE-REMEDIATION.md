# DWCO 0.4 acceptance remediation contract

CONTRACT_ID=DWCO-0.4-ACCEPTANCE-REMEDIATION

STATUS=AUTHORIZED_BOUNDED_REMEDIATION

BASELINE=MAIN_19680CD

DEPLOYMENT_STATUS=NOT_AUTHORIZED

## Purpose

Resolve the High/Major findings raised during independent DWCO 0.4 acceptance review without
expanding the product stage or changing the durable HTTP messaging contract.

## Authorized changes

1. End database authorization sessions before WebSocket acceptance and prove that repeated/live
   connections do not hold the bounded SQLAlchemy pool.
2. Revalidate tenant, user, membership, and permission state before each subsequent server fan-out.
   Disconnect an inactive context; refresh permissions before permission-filtered delivery; contain
   an authorization-store failure per connection so a post-commit fan-out cannot fail the HTTP
   mutation response.
3. On each mobile `realtime.ready` event, use authenticated, bounded `after_sequence` HTTP history
   pages to catch up the currently open conversation, deduplicate by server message ID, and restore
   server sequence order. Retry one transient request failure and surface an explicit error if the
   1,000-message safety cap is reached instead of silently presenting a gap.
4. Add backend and mobile regression tests and make mobile tests mandatory in local and remote CI.
5. Record the initial independent findings, remediation evidence, residual risks, and re-review.

```mermaid
sequenceDiagram
    participant M as Mobile client
    participant H as HTTP authority
    participant W as WebSocket hub
    participant D as Database

    M->>H: Request one-time realtime ticket
    M->>W: Connect with ticket
    W->>D: Short-lived authorization check
    D-->>W: Active context + current permissions
    Note over W,D: DB session closes before socket acceptance
    W-->>M: realtime.ready
    M->>H: Catch up open conversation history
    H-->>M: Durable sequenced messages
    W->>D: Revalidate before later fan-out
    alt Context revoked
        W-->>M: Disconnect; no event delivered
    else Context active
        W-->>M: Best-effort live event
    end
```

## Invariants

- HTTP remains authoritative for durable commands and reconnect catch-up.
- A WebSocket never owns a request-scoped database session for its lifetime.
- Revoked membership or inactive tenant/user state cannot receive a subsequent fan-out.
- Permission changes take effect before permission-filtered fan-out.
- Message content, credentials, and raw realtime tickets are not added to logs or metrics.
- Tenant isolation, message retention, history bounds, and existing application behavior remain.

## Required evidence

- Bounded-pool regression proving zero checked-out connections after authorization.
- Revoked-membership disconnect and refreshed-permission fan-out tests.
- Mobile gap-fill, deduplication, and sequence-order tests.
- Backend lint/format/types/tests; admin regressions; mobile types/tests/Expo check; workflow and
  repository validation; full local CI and Docker readiness.
- Independent Architecture, Identity/Security, QA/Validation, and DevOps/SRE re-review.

## Ownership

ACCOUNTABLE=Implementation Director

RESPONSIBLE=Backend,Realtime,Mobile

REQUIRED_REVIEWERS=Architecture,Identity/Security,QA/Validation,DevOps/SRE

CONSULTED=Integration,Admin Web

## Exclusions

No DWCO 0.5 work, shared broker, production deployment, PSTN/SIP/PBX, WebRTC media, eSIM, AI,
billing, provider credentials, or production data is authorized.

## Rollback

Revert the remediation commit. There is no schema migration. The pre-remediation DWCO 0.4 behavior
remains available on `main`, but the stage must stay unaccepted because the review findings would
reopen.
