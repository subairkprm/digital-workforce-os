# DWCO 0.5 voice adversarial and lifecycle matrix

STATUS=PROPOSED_FOR_QA_SECURITY_AND_OPERATIONS_REVIEW

IMPLEMENTATION_AUTHORIZED=NO

| ID | Scenario | Required assertion | Owner | Independent reviewer |
|---|---|---|---|---|
| V01 | Valid A calls B | One call/two active same-tenant participants; B rings; no media before acceptance | Backend + Mobile | QA + Security |
| V02 | B accepts | One authoritative accepted/connecting transition; media starts only after consent | Voice + Mobile | QA + Security |
| V03 | B declines | Terminal declined; no signal reuse, capture, or TURN continuation | Backend + Voice | QA |
| V04 | A cancels while ringing | Terminal cancelled; late accept rejected | Backend | QA |
| V05 | Either participant ends | Idempotent terminal end; peer notified; tracks, timers, and allocation released | Voice + Backend | QA + SRE |
| V06 | Ring timeout | Missed at 45 seconds; late commands rejected | Backend | QA |
| V07 | Simultaneous cross-call glare | First transaction wins one pair/call; loser catches up without double media | Backend + Voice | Architecture + QA |
| V08 | Duplicate/lost-response command or signal | Same proof/command retry recovers outcome/version; changed proof/payload conflicts; no duplicate side effect | Backend | QA + Security |
| V09 | Out-of-order/replayed signal | Stale generation/revision rejected; terminal call never revives | Backend + Realtime | QA + Security |
| V10 | Unauthorized client event | Generic publish, wrong role/call-leg, or foreign target rejected without disclosure | Realtime | Security |
| V11 | Cross-tenant ID substitution | Every call/signal/status/history/credential path denies and emits zero fan-out | Backend + Realtime | Security + QA |
| V12 | Same-tenant nonparticipant/admin | Cannot inspect/control/signal; admin cannot access SDP/audio | Backend + Admin Web | Security |
| V13 | Membership/user/tenant revoked mid-ring | Later command/event denied within 15 seconds; call ends/expires safely | Identity + Realtime | Security + QA |
| V14 | Permission removed mid-call | Fresh authority blocks delivery; teardown and five-minute relay hard limit measured | Identity + Realtime | Security |
| V15 | Microphone denied/revoked | No capture/transmission; explicit UX; no false media-ready state | Mobile + Voice | QA + Security |
| V16 | App backgrounds while ringing | No auto-answer; resources close; resume catches current state | Mobile | QA |
| V17 | App backgrounds while connected | Foreground-only policy closes media; resume never claims phantom active state | Mobile + Voice | QA |
| V18 | WebSocket drops around transition | Fresh ticket plus HTTP state/signal catch-up restores authority; duplicates harmless | Mobile + Realtime | QA |
| V19 | Signal window exceeded | Explicit resynchronization-required; no silent truncation | Mobile + Backend | QA |
| V20 | TURN UDP unavailable | TURN/TCP connects or call fails explicitly within 60 seconds | Voice + SRE | QA |
| V21 | Relay-only success | Two peers establish Opus DTLS-SRTP with no host/srflx candidate path | Voice + SRE | QA + Security |
| V22 | TURN credential expiry/reuse | Expired/wrong-call-leg credential denied; bounded same-leg reuse until expiry obeys quotas; no secret logged | Voice + Integration | Security |
| V23 | TURN/provider outage | New issue/allocation fails closed; HTTP state and unrelated features remain consistent | Integration + SRE | QA + Security |
| V24 | Candidate flood/oversize SDP | Contract byte/count/rate bounds reject without resource exhaustion | Backend + Realtime | Security + QA |
| V25 | Slow consumer/backpressure | Bounded disconnect/drop; HTTP recovery remains complete | Realtime | QA + SRE |
| V26 | Latency/loss/jitter/network switch | Outcomes match impairment matrix; restart or failure cleans resources | Voice + Mobile | QA |
| V27 | Multiple signed-in devices | Bound caller/first callee call legs alone signal and obtain credentials | Architecture + Identity | Security + QA |
| V28 | Storage/telemetry inspection | No audio, SDP, candidate, IP, TURN secret/credential, token, or device label | Security + SRE | Security + QA |
| V29 | Retention expiry/purge | Thirty-day boundary, tenant scope, permission, audit, and idempotency pass | Backend | Security + QA |
| V30 | Spam/concurrency/admission attack | Actor/target/user/pair limits and 20-call burst reject safely | Backend + SRE | Security + QA |
| V31 | Limiter/Redis unavailable | Call initiation, signaling, and credential issue fail closed without auth bypass | Backend + SRE | Security |
| V32 | Kill switch/rollback | New work blocked; active calls drain/end; ephemeral state clears; 0.1-0.4 remains green | DevOps/SRE | QA + Security |

Critical stop conditions are cross-tenant or nonparticipant disclosure/control, media before consent,
plaintext/downgraded media, sensitive media/token/secret logging, or rollback damage to unrelated
data. High stop conditions include stale authorization delivery, terminal-call revival, reusable or
leaked credentials, fail-open critical dependencies, or missing kill-switch cleanup. Any stop finding
blocks merge, stage credit, shared use, and deployment.
