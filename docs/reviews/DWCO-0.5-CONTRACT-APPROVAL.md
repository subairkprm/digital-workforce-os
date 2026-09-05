# DWCO 0.5 app-to-app voice/WebRTC contract approval

REVIEW_STATUS=BLOCKED_PRE_IMPLEMENTATION_DECISIONS_OPEN

CONTRACT_REVIEW_TARGET=6A7456B

RUNTIME_SELECTION_REVIEWED_TARGET=A4AF1DB

RUNTIME_SELECTION_REVIEW_DECISION=FAIL_CORRECTED_PROPOSAL_REVIEW_OPEN

STAGE_CREDIT=UNCHANGED_AT_48_PERCENT_OVERALL

DEPLOYMENT_STATUS=NOT_AUTHORIZED_NOT_DEPLOYED

IMPLEMENTATION_STATUS=NOT_AUTHORIZED_NOT_STARTED

## Acceptance evidence

| Gate | Result | Evidence or remaining action |
|---|---|---|
| Bounded product scope | Open; draft reviewed | `docs/implementation-contracts/DWCO-0.5-APP-VOICE-WEBRTC-CONTRACT.md`; Implementation Director decision required |
| Architecture decision | Pass at `6a7456b`; downstream blockers retained | Seven ADRs and call-leg recovery are coherent for the bounded local package; no implementation authorization |
| Identity/Security and privacy | Core contract pass at `a4af1db`; corrected runtime review open | VBL-03 and Security portion of VBL-07 may close; review minimal native configuration, manifest stop rules, coturn topology, and secret lifecycle |
| QA/Validation plan | Design pass at `a4af1db`; corrected runtime review open | VBL-06 may close for design only; review clean-prebuild allowlist, corrected fixture, device/NAT matrix, and manifest |
| DevOps/SRE boundary | Pass with blockers at `a4af1db` | Review corrected private-LAN/NAT, numeric user, tmpfs and secret-cleanup proposal; executable proof remains pre-merge |
| Implementation Director approval | Open | Approve the final contract and named owners/reviewers before development |

## Review findings

Residual risks are explicit:

- DEP-001 remote GitHub CI and branch protection remain unresolved.
- TURN/WebRTC infrastructure, capacity, observability, and network-failure evidence do not exist.
- PSTN, SIP/PBX, phone numbers, emergency calling, recording, and production calling remain excluded.
- Production deployment, provider credentials, and production data remain unauthorized.
- A digest-pinned coturn runtime and hardening/resource configuration are proposed but not approved
  or proven.
- A licence-clean native WebRTC bridge, project-owned minimal CNG configuration, and supported
  iOS/Android development-build matrix are proposed but not approved or proven.
- Coturn REST/HMAC provides bounded rather than immediate revocation of an existing hostile relay
  allocation; the proposed local hard limit is five minutes and shared/production use remains blocked.
- The initial `a4af1db` native pair was rejected because the external Expo plugin unconditionally
  expanded camera, overlay, wake-lock, Bluetooth, and iOS camera-description surfaces. The corrected
  proposal rejects that plugin, requires a minimal project-owned CNG plugin, removes the bridge's
  media-projection service, and adds generated-manifest stop tests.
- The initial coturn proposal could not support physical peers over loopback and omitted advertised
  Docker/NAT, numeric-user, and exact secret-lifecycle decisions. The corrected proposal uses a
  dedicated offline private LAN and explicit static bridge/address mapping, UID/GID, tmpfs, and
  interruption-safe scoped cleanup; it remains unapproved and unproven.

## Independent draft review

| Reviewer | Draft finding | Required next action |
|---|---|---|
| Architecture + Mobile/Voice | Architecture passed at `6a7456b`; native pair failed at `a4af1db` | Review corrected project-owned plugin, manifest stop rules, package/build/device proof; VBL-04 remains open |
| Identity/Security | Core contract pass; runtime selection failed at `a4af1db` | VBL-03 and Security portion of VBL-07 may close; review corrected least-privilege native/runtime proposal |
| QA/Validation | Test design pass; runtime selection failed at `a4af1db` | VBL-06 may close for design only; review clean-prebuild allowlist and corrected fixture; VBL-04 remains open |
| DevOps/SRE | Pass with blockers at `a4af1db` | Review corrected reachability/NAT/user/secret decisions; VBL-05 and DEP-001/DEP-007/DEP-012 remain open |

## Approval boundary

This gate authorizes contract drafting and review only. It does not authorize DWCO 0.5
implementation. Implementation may begin only after every gate above passes and a bounded contract
records owners, exclusions, tests, rollback, and deployment status.
