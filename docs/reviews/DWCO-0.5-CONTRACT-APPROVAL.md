# DWCO 0.5 app-to-app voice/WebRTC contract approval

REVIEW_STATUS=BLOCKED_PRE_IMPLEMENTATION_DECISIONS_OPEN

STAGE_CREDIT=UNCHANGED_AT_48_PERCENT_OVERALL

DEPLOYMENT_STATUS=NOT_AUTHORIZED_NOT_DEPLOYED

IMPLEMENTATION_STATUS=NOT_AUTHORIZED_NOT_STARTED

## Acceptance evidence

| Gate | Result | Evidence or remaining action |
|---|---|---|
| Bounded product scope | Open; draft reviewed | `docs/implementation-contracts/DWCO-0.5-APP-VOICE-WEBRTC-CONTRACT.md`; Implementation Director decision required |
| Architecture decision | Open; proposed ADRs ready | `docs/architecture/DWCO-0.5-WEBRTC-ARCHITECTURE.md` and seven proposed ADRs require exact-commit acceptance |
| Identity/Security and privacy | Open; threat model ready | `docs/security/DWCO-0.5-VOICE-THREAT-MODEL.md`; consent, revocation, abuse, and retention require acceptance |
| QA/Validation plan | Open; criteria ready | `docs/testing/DWCO-0.5-VOICE-VALIDATION-PLAN.md`; dependency/device/runtime evidence cannot exist before implementation |
| DevOps/SRE boundary | Open; blocked on selections | Pin coturn digest, ports, resource caps, authenticated readiness, isolation, and cleanup before approval |
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
| Architecture | Boundary recommended; decisions required | Accept or amend ADR-005-01 through ADR-005-07 against exact commit |
| Identity/Security | Criteria and adversarial matrix supplied | Accept or amend threat model, consent, revocation, retention, and authorization matrix |
| QA/Validation | Criteria and 32-scenario guidance supplied | Reconcile final contract to executable test IDs after dependency/runtime choices |
| DevOps/SRE | Blocked for implementation approval | Close VBL-04/VBL-05 and approve measurable local runtime before coding |

## Approval boundary

This gate authorizes contract drafting and review only. It does not authorize DWCO 0.5
implementation. Implementation may begin only after every gate above passes and a bounded contract
records owners, exclusions, tests, rollback, and deployment status.
