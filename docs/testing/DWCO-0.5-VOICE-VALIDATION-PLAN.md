# DWCO 0.5 voice validation plan

STATUS=DRAFT_FOR_QA_SECURITY_AND_DEVOPS_REVIEW

IMPLEMENTATION_AUTHORIZED=NO

## Acceptance layers

| Layer | Required proof |
|---|---|
| State-machine unit | Every valid transition; every invalid transition denied; terminal immutability; monotonic version |
| API integration | Tenant/participant authority, idempotency, stale version, bounds, retention, aggregate admin privacy |
| Realtime integration | Server-only event fan-out, reconnect HTTP catch-up, revocation, backpressure, store outage containment |
| Mobile controller | Permission, ring/accept/decline/cancel/end, mute, background/foreground, ICE restart, explicit errors |
| Two-client media | Relay-only encrypted audio establishes through local coturn with no direct candidate path |
| Network impairment | Deterministic thresholds and outcomes under latency, jitter, loss, disconnect, and TURN failure |
| Operations | Isolated Docker lifecycle, health/readiness, resource limits, content-free telemetry, rollback |
| Regression | All accepted DWCO 0.1–0.4 tests/builds/audits/migrations and governance health remain passing |

## Acceptance criteria

| ID | Required assertion |
|---|---|
| QA-01 | Contract, seven ADRs, threat model, supported development-build matrix, pinned dependencies, limits, rollback, and exact reviewers are approved before code |
| QA-02 | Migration upgrade/downgrade/re-upgrade and database constraints pass on disposable data without DWCO 0.1–0.4 regression |
| QA-03 | Ring, accept, decline, caller cancel, either-party end, missed, negotiation failure, reconnect, and duration cap reach exactly one documented state |
| QA-04 | Invalid actor/state/call-leg/version commands fail without partial mutation; terminal state is immutable |
| QA-05 | Lost-response retries with the same client proof/command are idempotent; changed proof/payload conflicts; simultaneous A-to-B/B-to-A glare produces one call |
| QA-06 | Signaling is ordered and bounded; malformed, oversize, duplicate, stale, wrong-role, and expired data is rejected; HTTP recovers missed events |
| QA-07 | Real peers establish encrypted audio through TURN/UDP and TURN/TCP; expiry, bounded credential reuse, outage, exhaustion, loss, latency, jitter, switch, and restart are deterministic |
| QA-08 | Clean Expo prebuilds match the approved Android permission/feature/service/provider and iOS usage-description/entitlement allowlists, then supported development builds prove permission, foreground/background, interruption, bound-call-leg, reconnect/relaunch, route, mute, and cleanup behavior |
| QA-09 | User/membership/tenant revocation blocks later commands and delivery within 15 seconds; cooperative teardown and five-minute relay hard limit are measured |
| QA-10 | Cross-tenant/nonparticipant ID substitution across every endpoint/event reveals no foreign identifier or signaling content |
| QA-11 | Retention/purge is tenant-scoped, audited, idempotent; DB/log/trace/metric/audit/crash/mobile inspection finds no prohibited data |
| QA-12 | Rate, concurrency, payload, candidate, queue, TURN allocation, resource, and backpressure limits fail closed without affecting messaging/presence |
| QA-13 | Exact-tree fast/full/Docker, clean-prebuild manifest-diff, audits, native build, migration, regression, secret scan, image/dependency scan, and governance pre/post health pass |
| QA-14 | Content-free metrics and stable opaque correlation identify setup latency, state/result, route category, failures, quality buckets, and resource saturation |
| QA-15 | Default-off kill switch blocks new calls/signals/credentials; bounded calls drain/end; ephemeral data/resources clear; unrelated 0.1–0.4 stays healthy |
| QA-16 | Completion evidence maps every test to result/artifact/SHA/reviewer and states remote CI, residual risk, no deployment, and deferred scope truthfully |

Any missing, failed, flaky, or not-run required test; unresolved Critical/High finding; scope
expansion; reviewer self-approval; or evidence not tied to the exact commit blocks merge and stage
credit.

## Required adversarial matrix

The executable ownership and reviewer map is in
[`DWCO-0.5-VOICE-ADVERSARIAL-MATRIX.md`](DWCO-0.5-VOICE-ADVERSARIAL-MATRIX.md).

- Cross-tenant call ID, conversation ID, history, signal, TURN credential, and admin-metric attempts.
- Non-participant initiate/accept/decline/end/signal and client-supplied tenant/user spoofing.
- Suspended membership or inactive tenant/user before initiate, while ringing, connecting, and active.
- Replayed command ID, reused client call ID with changed payload, stale version, simultaneous accept/end,
  simultaneous cross-call glare, duplicate WebSocket event, and out-of-order signaling envelope.
- Oversized/malformed SDP, excessive ICE candidates, unsupported media/video lines, stale signal TTL,
  credential expiry/bounded reuse, TURN realm mismatch, and relay allocation abuse.
- Redis, PostgreSQL, WebSocket, and TURN outage before and after a durable lifecycle commit.
- Queue overflow, client disappearance, 45-second ring expiry, 60-second negotiation expiry, four-hour
  duration cap, and 30-day metadata expiry/purge.
- Verify logs, traces, metrics, notifications, audits, and admin responses contain no media, transcript,
  SDP, candidates, raw credentials, IP address, or precise device/network identifiers.
- Fail clean-prebuild output containing Android camera/video feature or permission,
  `SYSTEM_ALERT_WINDOW`, `WAKE_LOCK`, media-projection service, unapproved foreground/background
  service/provider, or iOS camera usage description/entitlement. Verify API-scoped Bluetooth entries
  and the exact approved microphone/audio/network allowlist.

## Network impairment matrix

| Scenario | Local injection | Expected result |
|---|---|---|
| Baseline TURN/UDP | No injected fault; 20 attempts | 20/20 establish within 15 seconds and remain active 120 seconds; zero direct candidates or unexpected disconnects |
| Baseline TURN/TCP | Block TURN UDP; 20 attempts | At least 19/20 establish over TCP 3478 within 20 seconds and remain active 120 seconds; no attempt is non-terminal after 60 seconds |
| 50 ms RTT, 1% loss, 10 ms jitter | Isolated impairment helper; 20 attempts | At least 19/20 establish within 20 seconds and remain active 120 seconds |
| 150 ms RTT, 3% loss, 20 ms jitter | Isolated impairment helper; 20 attempts | At least 19/20 establish within 20 seconds and remain active 120 seconds; coarse degraded bucket recorded |
| 300 ms RTT, 5% loss, 50 ms jitter | Isolated impairment helper; 20 attempts | At least 18/20 establish within 30 seconds and remain active 60 seconds; every failure becomes terminal within 60 seconds |
| TURN unavailable | Stop isolated coturn; 20 attempts | 20/20 reject/fail terminal within 60 seconds; no direct ICE or peer-address exposure |
| WebSocket disconnected | Close event channel for 10 active calls | Media has zero unexpected disconnects; fresh ticket and HTTP catch-up converge within 5 seconds |
| Five-second media interruption | Drop relay traffic then restore; 20 attempts | At least 19/20 ICE restarts return active within 15 seconds; every other attempt fails terminal within 60 seconds |
| App backgrounds or process resumes | Controlled app lifecycle; 10 calls/state | Tracks close within 5 seconds; controlled background ends within 10 seconds; killed client times out within 60; foreground shows authoritative terminal state |
| Credential expires/reuses | Advance clock and reuse on 20 attempts | Existing allocation may live to five-minute cap; every new expired/wrong-leg allocation is denied; bounded same-leg use obeys quota |
| Relay ports exhausted | Constrain approved test range | New admission rejects within 5 seconds; established calls, messaging, presence, and governance remain healthy |
| Capacity/admission | 10 concurrent calls for 30 minutes, then 20-call burst | Ten calls remain active; excess rejects within 5 seconds; no limit exceeds 80% for over 5 minutes and recovery reaches baseline within 2 minutes |

These thresholds are configuration-backed assertions. A selected platform may add stricter profiles,
but cannot weaken them without contract amendment. Manual demonstrations supplement automation but
cannot replace it.

## Local observability contract

- Emit only enum-bounded state/result/failure and `turn_udp|turn_tcp|unknown` route, setup/recovery
  duration, coarse loss/jitter/RTT bucket, allocation count, aggregate bytes, and container resource
  utilization. Never label metrics by user, call, raw tenant, device, credential, IP, or candidate.
- The local evidence sink retains sanitized metrics for at most 24 hours and exports the manifest
  artifact only. DevOps/SRE and QA have local read access; there is no customer/admin telemetry UI.
- Each metric has at most 20 label combinations. Fail the gate for any valid-suite TURN auth error,
  relay exhaustion outside its explicit test, more than 5% baseline setup failure, p95 setup over
  15 seconds for UDP or 20 seconds for TCP, any unexpected direct route, or CPU/memory/PID/file-
  descriptor utilization above 80% of the approved limit for five consecutive minutes.
- The contract does not define shared/staging alerts or SLOs; DEP-012 remains required.

## Evidence package

- Machine-readable test results and coverage.
- Sanitized two-client state timeline and relay-only candidate proof.
- Resource/bandwidth observations for the bounded local concurrency target.
- Failure-injection results, retained known gaps, and exact immutable commit.
- Architecture, Identity/Security, QA/Validation, and DevOps/SRE decisions.
- Explicit `DEPLOYMENT_STATUS=NOT_AUTHORIZED_NOT_DEPLOYED`.
- Completed [`DWCO-0.5-EVIDENCE-MANIFEST.md`](DWCO-0.5-EVIDENCE-MANIFEST.md) with hashes and redaction
  review for every artifact.

## Evidence ownership

Voice/WebRTC, Backend, Mobile, and Realtime produce evidence. Identity/Security independently reviews
SEC/privacy/adversarial results; DevOps/SRE reviews runtime, isolation, readiness, capacity, and
rollback; QA/Validation reconciles every QA ID and exact SHA. The Implementation Director cannot
replace a missing independent result.
