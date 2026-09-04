# ADR-005-05: consent, authorization, and privacy

STATUS=PROPOSED

Server context supplies tenant, user, active membership, direct-conversation participation, call
role, and call leg on every command, read, credential issue, and event fan-out. Exactly
two distinct active same-tenant members participate. Foreign or nonparticipant resources receive a
non-enumerating denial.

The callee deliberately accepts only after microphone permission succeeds; ringing and operating-
system permission alone are not consent. No microphone audio is acquired or sent before acceptance.
No administrator can access media or signaling.

Participant call metadata is retained 30 days, then removed by a tenant-scoped, permissioned,
audited, idempotent purge. Approved fields are opaque call ID, participants, coarse timestamps,
terminal reason, duration, relay transport category, and coarse quality buckets. Audio, SDP, ICE,
IPs, credentials, tokens, and device labels are prohibited from durable or observability surfaces.

Revocation blocks commands and event delivery within 15 seconds. Cooperative clients tear down
within five seconds; a hostile relay allocation can persist no longer than its five-minute hard
lifetime. That residual local-only limit blocks shared or production use without stronger revocation.

The local voice feature is enabled only by a default-off server configuration flag plus explicit
tenant allowlist maintained by DevOps/SRE under reviewed configuration and restart. DWCO 0.5 adds no
runtime admin mutation. A future runtime tenant setting requires permission, cross-tenant denial,
audit, and a separate contract amendment.

Participant `GET /calls` is the only bounded export: opaque cursor, 50 approved metadata records per
page, and the 30-day retention window. Administrator/bulk export is deferred.
