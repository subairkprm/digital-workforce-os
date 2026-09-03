# Dependency register

| ID | Dependency | State | Impact | Owner | Exit evidence |
|---|---|---|---|---|---|
| DEP-001 | GitHub Actions account/workflow startup | Blocked externally | No remote CI attestation | DevOps/SRE | Successful run and protected required checks |
| DEP-002 | Local CI fallback | Active mitigation | Trusted-machine evidence only | DevOps/SRE + QA | Maintain until DEP-001 closes |
| DEP-003 | Realtime transport decision | Approval required | Blocks full DWCO 0.4 design | Architecture + Realtime | Approved ADR/contract |
| DEP-004 | Message persistence/delivery semantics | Approval required | Blocks schema/API acceptance | Backend + Realtime | Approved model and failure semantics |
| DEP-005 | Retention, deletion, privacy, abuse policy | Approval required | Blocks communication data | Identity/Security | Approved policy and tests |
| DEP-006 | Push provider/credentials | Not selected | Blocks background mobile delivery | Mobile + Integration | Approved adapter/environment plan |
| DEP-007 | TURN/WebRTC infrastructure | Not started | Blocks production app voice | Voice/WebRTC + DevOps/SRE | Later approved contract |
| DEP-008 | Authorised PSTN/SIP/PBX provider | Not started | Blocks business telephony | Telecom/PBX + Integration | Provider/legal approval |
| DEP-009 | Carrier/eSIM provider | Not started | Blocks mobility provisioning | Mobility/eSIM + Integration | Provider/regulatory approval |
| DEP-010 | AI provider/data governance | Not started | Blocks AI capabilities | AI + Identity/Security | Approved evaluation/data contract |
| DEP-011 | Billing/payment provider and tax model | Not started | Blocks monetisation | Implementation Director + Integration | Approved commercial contract |
| DEP-012 | Dev/staging/production infrastructure | Not started | Blocks deployment | DevOps/SRE + Architecture | Approved operations contract |

Dependencies do not authorize work. Owners track readiness; the Implementation Director controls
which dependency may enter an approved contract.
