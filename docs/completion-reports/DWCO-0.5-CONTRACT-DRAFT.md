# DWCO 0.5 contract-draft completion report

REPORT_STATUS=DOCUMENTATION_PACKAGE_COMPLETE_PREIMPLEMENTATION_GATES_OPEN

CONTRACT_PACKAGE_COMMIT=6A7456B

RUNTIME_SELECTION_INITIAL_REVIEW_COMMIT=A4AF1DB

RUNTIME_SELECTION_INITIAL_DECISION=FAIL_AT_A4AF1DB_SUPERSEDED_BY_CORRECTED_REVIEW

RUNTIME_SELECTION_CORRECTED_REVIEW_COMMIT=1EB3140

RUNTIME_SELECTION_CORRECTED_DECISION=PASS_DESIGN_WITH_VBL_04_LICENSING_BLOCKER

STAGE_CREDIT=UNCHANGED_AT_48_PERCENT_OVERALL

IMPLEMENTATION_STATUS=NOT_AUTHORIZED_NOT_STARTED

DEPLOYMENT_STATUS=NOT_AUTHORIZED_NOT_DEPLOYED

## Outcome

The documentation-only DWCO 0.5 package defines a bounded local one-to-one, same-tenant,
foreground, relay-only audio/WebRTC stage. It creates no application behavior, schema, container,
credential, shared environment, customer traffic, or deployment. The package is ready for immutable
commit review. The corrected native and coturn technical designs have been reviewed, with VBL-05 and
VBL-06 accepted for design. VBL-04 remains open for repository/native/transitive licensing, all
executable proof remains open, and implementation/deployment are not authorized.

## Files changed

- Canonical status/boundary records: `MASTER_PROJECT_PLAN.md`, `PROJECT_STATUS.md`,
  `SCOPE_BOUNDARIES.md`, and `DEPENDENCY_REGISTER.md`.
- Contract and approval register:
  `docs/implementation-contracts/DWCO-0.5-APP-VOICE-WEBRTC-CONTRACT.md` and
  `docs/reviews/DWCO-0.5-CONTRACT-APPROVAL.md`.
- Architecture proposal and seven ADRs under `docs/architecture/` and
  `docs/architecture/decisions/`.
- Exact dependency, platform matrix, coturn digest, and local-runtime proposal in
  `docs/architecture/DWCO-0.5-RUNTIME-SELECTION.md`.
- Security threat model: `docs/security/DWCO-0.5-VOICE-THREAT-MODEL.md`.
- QA plan, 32-case adversarial/lifecycle matrix, and evidence-manifest template under
  `docs/testing/`.
- This contract-draft completion report.

## Inconsistencies resolved

- Corrected `SCOPE_BOUNDARIES.md` from DWCO 0.4 “pending acceptance” to accepted through 0.4,
  approximately 48%, with external CI/deployment exceptions retained.
- Separated reviewed DWCO 0.5 draft status from accepted stage credit; 0.5 contributes zero until
  implementation evidence, reviews, acceptance, and merge.
- Reconciled durable HTTP/PostgreSQL authority with best-effort WebSocket delivery; WebSocket
  signaling notifications are content-free and signal bodies are HTTP-fetched.
- Replaced undefined access-token session binding with a client-generated, 256-bit, digest-stored,
  memory-only call-leg proof. Same-proof idempotent retries recover lost responses while normal
  authentication and fresh membership checks remain mandatory.
- Replaced an unenforceable one-use TURN claim with explicit bounded reuse until five-minute expiry,
  exact issuance/allocation quotas, and the residual revocation limit.
- Reconciled `accepted`, `connecting`, media-ready, race, timeout, and terminal transitions with an
  exhaustive actor/state table and authoritative timeout reconciler.
- Defined cross-pair one-call-per-user enforcement through transactional reservation rows.
- Removed successful direct-route metadata from a relay-only design; only TURN UDP/TCP/unknown is
  allowed.
- Split pre-code design approvals from executable pre-merge tests, runtime proofs, rollback, and
  coexistence evidence so the gate is not circular.
- Defined signaling pagination/gap behavior, participant export, feature configuration authority,
  abuse limits, numeric impairment/capacity thresholds, observability limits, and artifact formats.
- Rejected the initial third-party Expo WebRTC config plugin after exact-source review found
  unavoidable camera, overlay, wake-lock, Bluetooth, and camera-description expansion. The corrected
  design uses a minimal checked-in CNG plugin, removes media projection, and fails clean prebuilds on
  any unapproved generated native surface.
- Replaced loopback-only coturn publication with a dedicated offline private-device LAN and explicit
  static Docker/NAT address mapping; fixed numeric identity, writable tmpfs, secret creation, and
  interruption-safe project-scoped cleanup requirements.

## Verification

- `git diff --check`: pass.
- Local Markdown path/link reconciliation across 53 files: pass.
- `./scripts/ci-local-fast.sh`: pass.
- Backend: lint/format/type checks and 35 tests passed.
- Admin Web: type check and 8 tests passed.
- Mobile: type check, 5 tests, and Expo dependency compatibility passed.
- Governance: 3 parser/API tests and repository/workflow safety passed.
- Native/runtime metadata: exact npm versions, integrity values, peer ranges, licences, coturn source
  tag/commit, and multi-architecture image digest resolved read-only; no package or image was installed,
  pulled, or run.
- Local native readiness inventory: Xcode 26.6 and Docker 29.7.2 are present; Java/Android tooling
  and CocoaPods were not detected, so no native build or device claim is made.
- Live governance after reconciliation: `/healthz` returned healthy; `/api/governance` retained 48%
  accepted, 48% implemented, current gate DWCO 0.5 contract approval, and no deployment. The open
  review count is derived live from this approval register.
- Remote GitHub CI: unresolved under DEP-001; no remote-pass claim is made.

## Independent review summary

Architecture passed the reconciled package with downstream blockers at `6a7456b` and explicitly
closed the call-leg lost-response issue. Identity/Security and QA/Validation passed the parent
package with blockers at `03da95d`; their focused `6a7456b` approval remains open. DevOps/SRE passed
the parent package with blockers and confirmed that DEP-001, DEP-007, and DEP-012 remain open.
No reviewer authorized implementation, shared use, deployment, or stage credit.

At `a4af1db`, Architecture/Mobile, Identity/Security, and QA rejected the native runtime pair because
the selected external Expo plugin violated the audio-only permission boundary. Security accepted the
core VBL-03 and its VBL-07 contract decisions; QA accepted VBL-06 test-design readiness only.
DevOps/SRE passed the coturn digest proposal with blockers for reachability/NAT, exact identity, and
secret lifecycle. This package now corrects those findings and requires a new exact-commit review.

At `1eb3140`, Architecture/Mobile and Identity/Security passed the corrected technical native design
with one retained VBL-04 licensing blocker: the repository has no declared project licence and the
installed bridge/native/transitive notices have not been reviewed. QA passed VBL-06 design and
DevOps/SRE passed VBL-05 design. All executable evidence, DEP-001, DEP-007, DEP-012, VBL-04, VBL-08,
implementation, deployment, and stage credit remain open or unauthorized.

## Remaining gaps

- Preserve merged `main` baseline `9188adc` (PR #25 DWCO 0.4 status closure) when reviewing and
  merging the DWCO 0.5 contract branch.
- Obtain an explicit licensing decision for repository-owned source; review the installed WebRTC
  package, embedded native binaries, transitive licences, and notices; establish the missing local
  Android/CocoaPods prerequisites. VBL-04 remains open.
- After separate Implementation Director authorization, implement and prove the accepted coturn
  design's hardening, secrets, quotas, ports, resources, authenticated readiness,
  multi-architecture behavior, and cleanup.
- Obtain final VBL-04 licensing/Security/Mobile approval and the Implementation Director's exact
  contract decision; technical Architecture, QA-design, and DevOps-design reviews are recorded.
- DEP-001, DEP-007, DEP-012, remote CI, branch protection, shared scale, staging, production,
  privacy/legal/provider approval, incident/abuse operations, and penetration testing remain open.

## Recommended next approval gate

Commit and publish this documentation-only review record. The next gate is a licensing decision for
repository-owned source plus an installed native/transitive licence-and-notice review to close
VBL-04. The Implementation Director may consider a bounded implementation branch only after that
gate passes and must record explicit authorization against the final contract commit. PSTN/SIP/PBX,
recording, AI, billing, eSIM, shared/staging environments, production credentials/data, and
deployment remain unauthorized.
