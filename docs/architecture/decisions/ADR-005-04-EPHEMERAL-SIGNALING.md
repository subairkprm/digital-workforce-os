# ADR-005-04: ephemeral signaling

STATUS=PROPOSED

An `EphemeralSignalingStore` adapter uses Redis only for bounded SDP/ICE envelopes keyed by tenant,
call, bound participant leg, ICE generation, and monotonically increasing revision. Each
envelope expires within 120 seconds and is removed on a terminal transition where practical.

HTTP POST is authoritative for accepted signals; authenticated HTTP GET with `after_revision`
returns the current ICE generation in ascending pages of at most 200 envelopes, at most three pages
and three retry attempts. Unsupported SDP type/media, oversize data, candidate excess,
wrong role/leg/state, stale generation, and replay are rejected. A gap beyond retained history
returns explicit resynchronization-required; it never silently truncates. Submission is limited to
120 envelopes per call leg/minute in addition to the per-generation candidate cap.

No envelope body appears in PostgreSQL, WebSocket payloads, audit/security details, logs, traces,
metrics, crash reports, or administrative views. Redis or limiter unavailability fails closed for
new signaling while durable call state and unrelated messaging remain available.
