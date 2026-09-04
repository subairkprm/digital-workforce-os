# Realtime and messaging local operations

## Runtime authority

PostgreSQL is authoritative for conversations, participants, messages, ordering, receipts, expiry,
and redaction. Redis stores only short-lived connection tickets and rate counters. The WebSocket hub
is process-local and provides best-effort live events; clients recover missed events through bounded
HTTP history ordered by `sequence_number`.

## Failure behavior

- Redis unavailable: readiness fails, new realtime tickets return `503`, existing process-local
  connections may continue, and durable HTTP history remains the recovery path. The inherited local
  mutation limiter is fail-open and must receive a separate production policy review.
- PostgreSQL unavailable: durable message commands/history fail and readiness reports unavailable;
  a live event is never treated as accepted without a committed message.
- Connection interruption: the mobile client closes in background, obtains a new one-time ticket in
  foreground, reconnects, and reloads history when a conversation is opened.
- Slow connection: a 100-event outbound queue is enforced; overflow disconnects the client so it can
  recover from durable history.
- Duplicate send: the same tenant/sender/client-message ID returns the persisted message when content
  and conversation match, returns `410` after retention expiry, or `409` when the idempotency key
  conflicts. The conversation row serializes sequence assignment; the idempotency check is repeated
  after acquiring that lock.
- Notification adapter failure: the accepted message remains committed and the response remains
  successful. A metadata-only failure event is logged; message bodies are never passed to the adapter.

## Data lifecycle

Messages expire 90 days after acceptance. Expired messages are excluded from participant history.
An actor with `message.retention.manage` may call
`POST /api/v1/messaging/admin/retention/purge`; the tenant-only count is audited without content.
Senders may redact their own content. Participant history is the only bounded export; there is no
tenant-wide or administrator content export in this stage.

## Local rollback

Stop local clients and back up any non-disposable database before rollback. Run
`alembic downgrade 0004_presence` to remove receipts, messages, participants, conversations, and the
two messaging permissions. Revert the DWCO 0.4 realtime source commit. No production rollback or
data migration is authorized.

## Deployment prohibition

This design has no shared broker, production secret plan, horizontal fan-out, provider push delivery,
or approved production abuse policy. It must not be deployed to a shared or production environment
without a separate operations contract and architecture/security review.
