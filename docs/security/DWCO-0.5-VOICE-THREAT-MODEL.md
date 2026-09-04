# DWCO 0.5 voice threat model

STATUS=PROPOSED_FOR_IDENTITY_SECURITY_REVIEW

IMPLEMENTATION_AUTHORIZED=NO

## Assets and trust boundaries

Protected assets are tenant membership, call/control state, consent, SDP/ICE, TURN credentials,
participant metadata, tokens, network addresses, and microphone media. Trust boundaries exist at
the mobile client, authenticated HTTP API, server-only WebSocket delivery, PostgreSQL, ephemeral
Redis store, and isolated coturn relay. Client claims and all signaling bodies are untrusted.

## Threats and mandatory controls

| Threat | Mandatory control | Stop severity |
|---|---|---|
| Cross-tenant/nonparticipant access | Server-derived tenant/actor, fresh membership and participant check on every action/fan-out, non-enumerating denial | Critical |
| Call control or signaling replay | Versioned monotonic state, command idempotency, digest-stored call-leg proof, ICE generation and revision | High |
| Media before consent | Permission then deliberate accept before capture/offer; no auto-answer | Critical |
| Plaintext/downgraded media | WebRTC DTLS-SRTP only; fingerprint validation; insecure RTP prohibited | Critical |
| Peer IP/candidate disclosure | Relay-only ICE; candidate/SDP absent from events, logs, durable stores, metrics, and admin UI | High |
| TURN theft or relay abuse | Five-minute call-leg-named HMAC credentials, bounded reuse until expiry, fresh authorization, exact quotas, rotation, secret redaction, fail closed | High |
| Spam/resource exhaustion | Actor/target initiation limits, one live call/user, payload/candidate/allocation/resource bounds and backpressure | High |
| Stale authorization | Revalidate every mutation/fan-out; disconnect delivery within 15 seconds; bounded relay expiry documented | High |
| Provider/store compromise or outage | Provider-neutral adapters, least data, no shared secret outside server, critical path fail closed | High |
| Sensitive observability/storage | Allowlisted metadata, redaction tests across DB/log/trace/audit/crash/mobile storage | Critical |
| Rollback bypass/data loss | Default-off kill switch, block new credentials/calls, drain/end, scoped cleanup, reviewed migration downgrade | High |
| Abuse/legal/privacy gap | No shared/production use until employee notice, retention/export, provider processing, incident and abuse policy approval | High |

## Residual risk

Coturn cannot guarantee immediate termination of a hostile already-authorized relay allocation under
the proposed local REST/HMAC design. Credentials and allocations are therefore capped at five
minutes, subsequent signaling is denied within 15 seconds, and shared/production use remains blocked
until Identity/Security accepts a stronger revocation design or the documented maximum.

Remote CI, branch protection, production abuse operations, provider data processing, legal/privacy
approval, and penetration testing are absent. Local contract approval cannot waive them.
