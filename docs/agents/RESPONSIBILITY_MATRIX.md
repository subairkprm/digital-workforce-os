# Responsibility and reviewer matrix

Legend: **A** accountable, **R** responsible, **V** required reviewer/validator, **C** consulted.

| Work area | A | R | V | C |
|---|---|---|---|---|
| Contract/stage acceptance | Implementation Director | Primary agent | Architecture, Identity/Security, QA/Validation | DevOps/SRE |
| Architecture/ADR | Architecture | Architecture | Identity/Security, QA/Validation | Affected agents |
| Backend/API/database | Implementation Director | Backend | Architecture, Identity/Security, QA/Validation | DevOps/SRE |
| Identity/RBAC/isolation | Identity/Security | Identity/Security + Backend | Architecture, QA/Validation | Admin Web, Mobile |
| Admin web | Implementation Director | Admin Web | Identity/Security, QA/Validation | Backend, Architecture |
| Mobile | Implementation Director | Mobile | Identity/Security, QA/Validation | Backend, Realtime |
| Realtime/messaging | Implementation Director | Realtime + Backend | Architecture, Identity/Security, DevOps/SRE, QA/Validation | Mobile, Admin Web |
| App voice/WebRTC | Implementation Director | Voice/WebRTC | Architecture, Identity/Security, DevOps/SRE, QA/Validation | Mobile, Realtime |
| PSTN/SIP/PBX | Implementation Director | Telecom/PBX + Integration | Architecture, Identity/Security, DevOps/SRE, QA/Validation | Voice/WebRTC |
| Mobility/eSIM | Implementation Director | Mobility/eSIM + Integration | Architecture, Identity/Security, QA/Validation | Mobile, DevOps/SRE |
| External integrations | Implementation Director | Integration | Architecture, Identity/Security, QA/Validation | Backend, DevOps/SRE |
| AI capability | Implementation Director | AI | Architecture, Identity/Security, QA/Validation | Backend, Integration |
| CI/environments/release | DevOps/SRE | DevOps/SRE | Identity/Security, QA/Validation | Architecture |
| Test/acceptance evidence | QA/Validation | QA/Validation | Relevant domain reviewer | Implementation Director |

Reviewer approval confirms documented criteria were evaluated; it does not authorize production.
