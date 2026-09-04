# Dependency register

| ID | Dependency | State | Impact | Owner | Exit evidence |
|---|---|---|---|---|---|
| DEP-001 | GitHub Actions account/workflow startup | Blocked externally | No remote CI attestation | DevOps/SRE | Successful run and protected required checks |
| DEP-002 | Local CI fallback | Active mitigation | Trusted-machine evidence only | DevOps/SRE + QA | Maintain until DEP-001 closes |
| DEP-003 | Realtime transport decision | Implemented and merged; acceptance pending | WebSocket tickets plus HTTP catch-up selected | Architecture + Realtime | DWCO 0.4 acceptance review |
| DEP-004 | Message persistence/delivery semantics | Implemented and merged; acceptance pending | Direct durable ordered messaging selected | Backend + Realtime | DWCO 0.4 acceptance review |
| DEP-005 | Retention, deletion, privacy, abuse policy | Implemented and merged; acceptance pending | 90-day expiry, sender redaction, bounded access | Identity/Security | DWCO 0.4 acceptance review |
| DEP-006 | Push provider/credentials | Deferred; null adapter active | No background provider delivery | Mobile + Integration | Separate provider/environment approval |
| DEP-007 | TURN/WebRTC infrastructure | Not started | Blocks production app voice | Voice/WebRTC + DevOps/SRE | Later approved contract |
| DEP-008 | Authorised PSTN/SIP/PBX provider | Not started | Blocks business telephony | Telecom/PBX + Integration | Provider/legal approval |
| DEP-009 | Carrier/eSIM provider | Not started | Blocks mobility provisioning | Mobility/eSIM + Integration | Provider/regulatory approval |
| DEP-010 | AI provider/data governance | Not started | Blocks AI capabilities | AI + Identity/Security | Approved evaluation/data contract |
| DEP-011 | Billing/payment provider and tax model | Not started | Blocks monetisation | Implementation Director + Integration | Approved commercial contract |
| DEP-012 | Dev/staging/production infrastructure | Not started | Blocks deployment | DevOps/SRE + Architecture | Approved operations contract |

Dependencies do not authorize work. Owners track readiness; the Implementation Director controls
which dependency may enter an approved contract.
