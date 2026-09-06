# ADR-005-03: local coturn boundary

STATUS=ACCEPTED_LOCAL_DESIGN_EXECUTABLE_PROOF_OPEN

An `IceServerProvider` adapter issues participant/call-leg-named TURN REST/HMAC credentials after
fresh authorization and a valid call-leg proof. Credentials live for at most five minutes, contain
an opaque call-leg identifier rather than PII, rotate for retry/new call, and never expose the shared
secret. Standard TURN REST/HMAC credentials may be reused by a holder until expiry and are not
claimed to be one-use or immediately revocable. Limits are three issues per leg/call, ten per
user/ten minutes, one allocation per leg credential, two per call, 24 per local tenant,
256 kbit/s per allocation, and 6 Mbit/s per local tenant. Five failed allocations/minute/source
triggers a ten-minute cooldown. Provider or limiter failure fails closed.

The proposed local voice-test Compose project is `dwco-voice-ci`, isolated from development,
governance, and normal `dwco-ci`. Listener 13478 UDP/TCP and relay UDP 49160-49259 are published
only on a selected RFC1918 host address on a dedicated offline test LAN; loopback-only physical proof,
wildcard/public binding, host networking, and public STUN are prohibited. The container must use
numeric UID/GID `65534:65534`, read-only root, no-new-privileges, no capabilities, bounded UID-owned
tmpfs, resource limits, and the selected digest.
Readiness requires a fresh authenticated allocation and relay probe from a separate test peer.

The candidate image digest, resource caps, secret injection, and collision-free rendered Compose
config and physical-peer Docker/NAT topology are fixed in
[`../DWCO-0.5-RUNTIME-SELECTION.md`](../DWCO-0.5-RUNTIME-SELECTION.md) and accepted for bounded
local design at `1eb3140`. Executable proof remains a pre-merge blocker. Runtime caps are 1 CPU,
256 MiB memory, 100 PIDs,
65,536 open files, and Docker log rotation of 10 MiB times three. Drop all Linux capabilities; run
as a documented non-root UID with read-only root and bounded tmpfs. A fresh secret file under the
repository's ignored `.env.dwco-voice-ci-turn-secret` path is mounted read-only through Docker
secrets, never placed in Compose/environment/process-argument output, and deleted by scoped,
interruption-safe cleanup. Proof that these settings work, including rendered config, readiness,
collision, NAT, and cleanup, is pre-merge evidence. TLS/TCP 5349, DNS, certificates, staging, and
production are deferred to a separate DEP-012 environment contract.
