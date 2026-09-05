# DWCO 0.5 app-to-app voice/WebRTC contract approval

REVIEW_STATUS=BLOCKED_PRE_IMPLEMENTATION_DECISIONS_OPEN

CONTRACT_REVIEW_TARGET=6A7456B

RUNTIME_SELECTION_REVIEWED_TARGET=A4AF1DB

RUNTIME_SELECTION_CORRECTED_REVIEWED_TARGET=1EB3140

RUNTIME_SELECTION_REVIEW_DECISION=PASS_WITH_VBL_04_LICENSING_BLOCKER

VBL_02=PASS_AT_6A7456B

VBL_03=PASS_AT_1EB3140

VBL_04=OPEN_PROJECT_AND_NATIVE_TRANSITIVE_LICENSING_DECISION

VBL_05=PASS_DESIGN_AT_1EB3140_EXECUTABLE_EVIDENCE_PREMERGE

VBL_06=PASS_DESIGN_AT_1EB3140_EXECUTABLE_EVIDENCE_PREMERGE

VBL_07=PASS_AT_1EB3140

VBL_08=OPEN_IMPLEMENTATION_AND_ENVIRONMENT_AUTHORIZATION

STAGE_CREDIT=UNCHANGED_AT_48_PERCENT_OVERALL

DEPLOYMENT_STATUS=NOT_AUTHORIZED_NOT_DEPLOYED

IMPLEMENTATION_STATUS=NOT_AUTHORIZED_NOT_STARTED

## Acceptance evidence

| Gate | Result | Evidence or remaining action |
|---|---|---|
| Bounded product scope | Open; draft reviewed | `docs/implementation-contracts/DWCO-0.5-APP-VOICE-WEBRTC-CONTRACT.md`; Implementation Director decision required |
| Architecture decision | Pass at `6a7456b`; downstream blockers retained | Seven ADRs and call-leg recovery are coherent for the bounded local package; no implementation authorization |
| Identity/Security and privacy | Core/privacy design pass at `1eb3140`; licensing blocker retained | VBL-03 and Security portion of VBL-07 pass; VBL-04 remains open for repository and installed native/transitive licensing decisions |
| QA/Validation plan | Design pass at `1eb3140` | VBL-06 design closes; all clean-prebuild, native, device, relay, failure, and regression evidence remains pre-merge |
| DevOps/SRE boundary | Design pass at `1eb3140` | VBL-05 design closes; all runtime/NAT/resource/secret/readiness/cleanup evidence remains pre-merge |
| Implementation Director approval | Open | Approve the final contract and named owners/reviewers before development |

## Review findings

Residual risks are explicit:

- DEP-001 remote GitHub CI and branch protection remain unresolved.
- TURN/WebRTC infrastructure, capacity, observability, and network-failure evidence do not exist.
- PSTN, SIP/PBX, phone numbers, emergency calling, recording, and production calling remain excluded.
- Production deployment, provider credentials, and production data remain unauthorized.
- A digest-pinned coturn runtime and hardening/resource design are accepted for the bounded local
  stage but remain unimplemented and unproven.
- A licence-clean native WebRTC bridge, project-owned minimal CNG configuration, and supported
  iOS/Android development-build matrix are technically accepted but not licence-approved or proven.
- The repository has no declared project licence. VBL-04 stays open until the Implementation Director
  obtains an explicit repository-owned-source licensing decision and Security reviews the actually
  installed WebRTC package, embedded native binaries, transitive licences, and notices.
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
| Architecture + Mobile/Voice | Technical selection pass with licensing blocker at `1eb3140` | Corrected native design accepted; VBL-04 remains open for licensing and later executable proof |
| Identity/Security | Core/privacy pass with licensing blocker at `1eb3140` | VBL-03 and Security portion of VBL-07 close; VBL-04 remains open for project/native/transitive licensing |
| QA/Validation | Design pass at `1eb3140` | VBL-06 design closes; executable evidence and QA-01 remain pre-merge blockers |
| DevOps/SRE | Design pass at `1eb3140` | VBL-05 design closes; executable evidence plus DEP-001/DEP-007/DEP-012 remain open |

## Approval boundary

This gate authorizes contract drafting and review only. It does not authorize DWCO 0.5
implementation. Implementation may begin only after every gate above passes and a bounded contract
records owners, exclusions, tests, rollback, and deployment status.
