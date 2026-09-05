# DWCO 0.5 app-to-app voice/WebRTC contract approval

REVIEW_STATUS=BLOCKED_PRE_IMPLEMENTATION_DECISIONS_OPEN

CONTRACT_REVIEW_TARGET=6A7456B

STAGE_CREDIT=UNCHANGED_AT_48_PERCENT_OVERALL

DEPLOYMENT_STATUS=NOT_AUTHORIZED_NOT_DEPLOYED

IMPLEMENTATION_STATUS=NOT_AUTHORIZED_NOT_STARTED

## Acceptance evidence

| Gate | Result | Evidence or remaining action |
|---|---|---|
| Bounded product scope | Open; draft reviewed | `docs/implementation-contracts/DWCO-0.5-APP-VOICE-WEBRTC-CONTRACT.md`; Implementation Director decision required |
| Architecture decision | Pass at `6a7456b`; downstream blockers retained | Seven ADRs and call-leg recovery are coherent for the bounded local package; no implementation authorization |
| Identity/Security and privacy | Open; package passed with blockers at `03da95d` | Re-review the `6a7456b` call-leg amendment and accept threat model, proof, consent, revocation, abuse, and retention |
| QA/Validation plan | Open; package passed with blockers at `03da95d` | Re-review `6a7456b`, then accept fixtures, QA-01 through QA-16, V01 through V32, and manifest |
| DevOps/SRE boundary | Open; package passed with blockers at `03da95d` | Select/approve coturn digest, runtime configuration, readiness, isolation, and cleanup against final target |
| Implementation Director approval | Open | Approve the final contract and named owners/reviewers before development |

## Review findings

Residual risks are explicit:

- DEP-001 remote GitHub CI and branch protection remain unresolved.
- TURN/WebRTC infrastructure, capacity, observability, and network-failure evidence do not exist.
- PSTN, SIP/PBX, phone numbers, emergency calling, recording, and production calling remain excluded.
- Production deployment, provider credentials, and production data remain unauthorized.
- A digest-pinned coturn runtime and hardening/resource configuration are not selected.
- A license-clean native WebRTC dependency, supported iOS/Android development-build matrix, and
  reproducible two-device path are not selected or proven.
- Coturn REST/HMAC provides bounded rather than immediate revocation of an existing hostile relay
  allocation; the proposed local hard limit is five minutes and shared/production use remains blocked.

## Independent draft review

| Reviewer | Draft finding | Required next action |
|---|---|---|
| Architecture | Pass with blockers at `6a7456b`; lost-response blocker closed | VBL-02 and Architecture portion of VBL-07 accepted; retain downstream gates |
| Identity/Security | Pass with blockers at `03da95d`; final focused review open | Review `6a7456b`, selected native dependency/coturn, and formally record VBL-03/VBL-07 |
| QA/Validation | Pass with blockers at `03da95d`; final focused review open | Review `6a7456b`, then accept selected fixtures/runtime and VBL-06 |
| DevOps/SRE | Pass with blockers at `03da95d` | Close VBL-05 and re-affirm DEP-001/DEP-007/DEP-012 at final target |

## Approval boundary

This gate authorizes contract drafting and review only. It does not authorize DWCO 0.5
implementation. Implementation may begin only after every gate above passes and a bounded contract
records owners, exclusions, tests, rollback, and deployment status.
