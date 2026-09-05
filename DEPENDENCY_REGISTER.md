# Dependency register

| ID | Dependency | State | Impact | Owner | Exit evidence |
|---|---|---|---|---|---|
| DEP-001 | GitHub Actions account/workflow startup | Blocked externally | No remote CI attestation | DevOps/SRE | Successful run and protected required checks |
| DEP-002 | Local CI fallback | Active mitigation | Trusted-machine evidence only | DevOps/SRE + QA | Maintain until DEP-001 closes |
| DEP-003 | Realtime transport decision | Resolved for bounded DWCO 0.4 | WebSocket tickets plus HTTP catch-up accepted | Architecture + Realtime | Review and remediation evidence at `607e6c0` |
| DEP-004 | Message persistence/delivery semantics | Resolved for bounded DWCO 0.4 | Direct durable ordered messaging accepted | Backend + Realtime | Review and remediation evidence at `607e6c0` |
| DEP-005 | Retention, deletion, privacy, abuse policy | Resolved for bounded DWCO 0.4 | 90-day expiry, sender redaction, bounded access accepted | Identity/Security | Review and remediation evidence at `607e6c0` |
| DEP-006 | Push provider/credentials | Deferred; null adapter active | No background provider delivery | Mobile + Integration | Separate provider/environment approval |
| DEP-007 | TURN/WebRTC infrastructure | Exact local candidates proposed; reviewer approval and proof open; implementation unauthorized | Blocks app voice implementation and production calling | Voice/WebRTC + DevOps/SRE | Approve `docs/architecture/DWCO-0.5-RUNTIME-SELECTION.md`, then provide bounded executable evidence; production remains separate |
| DEP-008 | Authorised PSTN/SIP/PBX provider | Not started | Blocks business telephony | Telecom/PBX + Integration | Provider/legal approval |
| DEP-009 | Carrier/eSIM provider | Not started | Blocks mobility provisioning | Mobility/eSIM + Integration | Provider/regulatory approval |
| DEP-010 | AI provider/data governance | Not started | Blocks AI capabilities | AI + Identity/Security | Approved evaluation/data contract |
| DEP-011 | Billing/payment provider and tax model | Not started | Blocks monetisation | Implementation Director + Integration | Approved commercial contract |
| DEP-012 | Dev/staging/production infrastructure | Not started | Blocks deployment | DevOps/SRE + Architecture | Approved operations contract |
| DEP-013 | Shared realtime broker and scalable revocation | Deferred; process-local hub active | Blocks shared/horizontal realtime | Architecture + Realtime + DevOps/SRE | Approved shared-environment contract and load/failure evidence |

Dependencies do not authorize work. Owners track readiness; the Implementation Director controls
which dependency may enter an approved contract.
