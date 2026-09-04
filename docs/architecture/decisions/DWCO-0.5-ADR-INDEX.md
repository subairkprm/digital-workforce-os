# DWCO 0.5 architecture decision index

STATUS=PROPOSED_FOR_REQUIRED_REVIEW

IMPLEMENTATION_AUTHORIZED=NO

These decisions lock the bounded design only after the named reviewers approve an exact commit.
They do not authorize code, shared infrastructure, credentials, or deployment.

| ADR | Decision | Required reviewers |
|---|---|---|
| [ADR-005-01](ADR-005-01-CONTROL-AUTHORITY.md) | HTTP/PostgreSQL control authority, state, races, and WebSocket role | Architecture, Identity/Security, QA |
| [ADR-005-02](ADR-005-02-MEDIA-BOUNDARY.md) | Audio-only WebRTC, relay privacy, codecs, and limits | Architecture, Identity/Security, Voice/WebRTC |
| [ADR-005-03](ADR-005-03-LOCAL-COTURN.md) | Provider-neutral local coturn and credential boundary | DevOps/SRE, Identity/Security, Architecture |
| [ADR-005-04](ADR-005-04-EPHEMERAL-SIGNALING.md) | Redis signaling schema, order, TTL, bounds, and recovery | Architecture, Identity/Security, Realtime |
| [ADR-005-05](ADR-005-05-CONSENT-PRIVACY.md) | Consent, authorization, metadata, retention, and revocation | Identity/Security, Product, QA |
| [ADR-005-06](ADR-005-06-MOBILE-LIFECYCLE.md) | Foreground native development-build lifecycle | Mobile, Voice/WebRTC, QA |
| [ADR-005-07](ADR-005-07-SHARED-SCALE-DEFERRAL.md) | Local single-instance boundary and future shared requirements | Architecture, DevOps/SRE, Realtime |

All seven remain proposed until `docs/reviews/DWCO-0.5-CONTRACT-APPROVAL.md` records their decisions.
