# ADR-005-01: voice control authority

STATUS=PROPOSED

Authenticated HTTP commands and PostgreSQL are the durable call-state authority. Mutations use a
server-derived tenant/actor, optimistic version, command idempotency, and transactional uniqueness
for each non-terminal participant pair. WebSocket emits server-only change notifications after a
commit; HTTP state and signaling catch-up recover every missed notification.

One non-terminal call per user is enforced with two `active_call_reservations` rows inserted in
sorted user-ID order in the same transaction as call creation; unique tenant-user keys prevent
cross-pair races. Terminal transitions delete both reservations transactionally. The first commit
wins glare or command/deadline races.

The single local API process runs an idempotent timeout sweep every five seconds and lazily
reconciles expiry before each call read/command. Row locking plus conditional version updates commit
ring, negotiation, reconnect, and four-hour deadlines once. Startup reconciliation precedes voice
readiness.

The legal state and actor transitions, timeouts, call-leg proof, glare winner, and terminal
immutability are normative in the DWCO 0.5 contract. A client event cannot commit state.

Consequence: the existing process-local hub is useful for low-latency local delivery but is never
represented as multi-instance authority or durability.
