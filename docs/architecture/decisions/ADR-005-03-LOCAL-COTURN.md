# ADR-005-03: local coturn boundary

STATUS=PROPOSED_BLOCKED_ON_PINNED_RUNTIME_REVIEW

An `IceServerProvider` adapter issues participant/call-leg-named TURN REST/HMAC credentials after
fresh authorization and a valid call-leg proof. Credentials live for at most five minutes, contain
an opaque call-leg identifier rather than PII, rotate for retry/new call, and never expose the shared
secret. Standard TURN REST/HMAC credentials may be reused by a holder until expiry and are not
claimed to be one-use or immediately revocable. Limits are three issues per leg/call, ten per
user/ten minutes, one allocation per leg credential, two per call, 24 per local tenant,
256 kbit/s per allocation, and 6 Mbit/s per local tenant. Five failed allocations/minute/source
triggers a ten-minute cooldown. Provider or limiter failure fails closed.

The proposed local voice-test Compose project is `dwco-voice-ci`, isolated from development,
governance, and normal `dwco-ci`. Proposed loopback ports are 13478 UDP/TCP with relay UDP
49160-49259; host networking and public STUN are prohibited. The container must be non-root where
supported, read-only, no-new-privileges, capability-minimized, resource-limited, and digest-pinned.
Readiness requires a fresh authenticated allocation and relay probe from a separate test peer.

The exact image digest, resource caps, secret injection, and collision-free rendered Compose config
remain DevOps/SRE approval blockers. Proposed runtime caps are 1 CPU, 256 MiB memory, 100 PIDs,
65,536 open files, and Docker log rotation of 10 MiB times three. Drop all Linux capabilities; run
as a documented non-root UID with read-only root and bounded tmpfs. A fresh secret file under the
repository's ignored `.env.dwco-voice-ci-turn-secret` path is mounted read-only through Docker
secrets, never placed
in Compose/environment output, and deleted by scoped cleanup. The exact repository/image digest and
proof that these settings work remain pre-code selection requirements; rendered config, readiness,
collision, and cleanup are pre-merge evidence. TLS/TCP 5349, DNS, certificates, staging, and production are
deferred to a separate DEP-012 environment contract.
