# DWCO 0.4 — Realtime communication contract

CONTRACT_STATUS=APPROVED_FOR_LOCAL_IMPLEMENTATION_AND_REVIEW

APPROVED_ON=2026-09-04

APPROVAL_SCOPE=BOUNDED_DEVELOPMENT_AND_REVIEW_ONLY

IMPLEMENTATION_STATUS=LOCAL_IMPLEMENTATION_COMPLETE_REVIEW_PENDING

## Objective

Extend the merged polling-based presence prerequisite into secure tenant realtime presence transport
and bounded workforce messaging without introducing voice, telecom, AI, billing, or production
deployment.

## In scope

- Authenticated realtime connections with server-derived tenant and membership context.
- Presence transport preserving existing ownership and 120-second expiry invariants.
- Tenant workforce direct messaging with approved persistence and delivery semantics.
- Bounded history, deterministic pagination, validation, and rate/size limits.
- Mobile foreground/background reconnection behavior and clear delivery-state UX.
- Admin access only where permissioned; no default message-content visibility.
- Migrations, provider-neutral notification boundary, observability events, and tests.
- Retention, deletion, export, failure-mode, and local-rollback documentation.

## Approved decisions

1. Use WebSocket for best-effort live events and authenticated HTTP for durable commands and
   catch-up. A one-time, Redis-backed connection ticket expires after 60 seconds; access and refresh
   tokens are never placed in a WebSocket URL. Reconnection obtains a new ticket and resumes through
   bounded sequence-based HTTP history.
2. Support direct conversations only. Each conversation contains exactly two distinct users with
   active memberships in the same server-verified tenant. Group, guest, public, and federated
   conversations are deferred.
3. Persist accepted messages before fan-out. Messages receive a per-conversation monotonic sequence;
   sender-provided client message IDs provide idempotency. Realtime delivery is best effort, offline
   delivery is durable history, and read receipts are explicit participant actions. No exactly-once
   network-delivery claim is made.
4. Messages receive a 90-day expiry. Expired content is excluded from history and may be purged by a
   permissioned, audited tenant maintenance action. Senders may redact their own messages. Participant
   history is the only bounded export in this stage; tenant-wide or administrative content export is
   deferred.
5. Provide a provider-neutral notification adapter with a no-op local implementation. Notifications
   carry identifiers only and never message bodies. No provider, credential, or background push
   delivery is authorized.
6. Limit message bodies to 4,000 characters, disallow attachments, cap history at 100 records, cap
   send mutations at 30 per minute per actor, cap realtime frames at 8 KiB, and cap each connection's
   outbound queue at 100 events. No content-reporting workflow is introduced in this stage.
7. Record structured connection, authorization, rate-limit, and aggregate messaging metadata without
   message content, raw tickets, credentials, or participant surveillance.
8. The enforced local fast/full/Docker gates remain mandatory while DEP-001 is open. Remote CI status
   must be reported truthfully and cannot be represented as passing. Merge remains a separate explicit
   repository decision after review.

## Security and privacy invariants

- Tenant and actor identity come only from verified server-side session context.
- Every subscription, publish, history, and receipt operation is tenant- and participant-authorized.
- Client-supplied tenant/user identifiers never establish authorization.
- Resume tokens are short-lived, scoped, revocable, and never logged raw.
- Logs, metrics, notifications, and traces exclude message bodies and credentials by default.
- History/fan-out are bounded; rate, connection, payload, and backpressure limits apply.
- Administrative metadata access is permissioned/audited; ordinary exchange is not an employee-
  surveillance audit stream.

## Explicitly out of scope

- PSTN, SIP, PBX, numbering, emergency calling, recording, and production WebRTC calling.
- eSIM, carrier APIs, and mobile-core operation.
- AI summarisation, classification, scoring, training, or communication inference.
- Billing, payments, subscriptions, production deployment, or production data migration.
- Unbounded attachments, public/federated messaging, and external guest communication.

## Ownership and review

ACCOUNTABLE=Implementation Director

RESPONSIBLE=Realtime,Backend,Mobile

REQUIRED_REVIEWERS=Architecture,Identity/Security,DevOps/SRE,QA/Validation

CONSULTED=Admin Web,Integration

## Acceptance criteria

- Required decisions are recorded here or in linked ADRs.
- Migration round-trip passes without behavior changes outside scope.
- Cross-tenant, unauthorized subscribe/publish/history, token expiry/revocation, reconnect,
  ordering/idempotency, bounds, rate-limit, and backpressure tests pass.
- Existing DWCO 0.1–0.4 presence regressions pass.
- Backend, admin, mobile, dependency audit, and Docker readiness gates pass.
- Remote CI is stated truthfully; local evidence is attached if DEP-001 remains open.
- Completion report, dependency updates, rollback, and deployment status are reviewed.

## Deployment boundary

DEPLOYMENT_STATUS=NOT_AUTHORIZED

Approval would authorize bounded development and review only. A separate operations/deployment
contract is required for any shared or production environment.

## Local implementation evidence

The review branch implements the approved direct-messaging, one-time-ticket WebSocket, mobile,
metadata-only admin, retention, notification-boundary, migration, and adversarial-test scope. The
completion report is `docs/completion-reports/DWCO-0.4-REALTIME-COMMUNICATION.md`. This evidence does
not authorize merge or deployment and does not update accepted stage weight.
