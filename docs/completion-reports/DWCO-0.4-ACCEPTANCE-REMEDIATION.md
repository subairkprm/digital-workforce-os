# DWCO 0.4 acceptance remediation completion report

CONTRACT_ID=DWCO-0.4-ACCEPTANCE-REMEDIATION

IMPLEMENTATION_EVIDENCE=539D07A_97E3664

STATUS=MERGED_TO_MAIN_ACCEPTED

ACCEPTED_WEIGHTED_COMPLETION=48_PERCENT_APPROXIMATE

DEPLOYMENT_STATUS=NOT_AUTHORIZED_NOT_DEPLOYED

## Files changed

- Backend realtime authorization/session lifetime, fan-out failure containment, forward history
  cursor, and Phase 5 regressions.
- Mobile reconnect controller, message reconciliation, lifecycle-oriented tests, package lock, and
  mandatory CI test commands.
- Local full/fast CI and hosted workflow definitions, including isolated Compose lifecycle and live
  governance coexistence checks.
- Governance evidence parser/tests and DWCO 0.4 remediation contract/review records.

## Inconsistencies resolved

- Removed the WebSocket-lifetime database session while retaining server-derived authority.
- Replaced stale established-socket authorization with pre-fan-out revalidation and fail-closed
  per-connection error containment.
- Replaced ticket-only mobile reconnect with authenticated, ascending, paginated HTTP catch-up.
- Replaced merge-helper-only QA evidence with multi-page gap, retry, cap, order, and dedup tests.
- Removed duplicate CI helper definitions and default-project Docker operations introduced while
  reconciling concurrent governance work.
- Corrected live dashboard review counting so fail, pending, open, and in-progress gates remain
  visible.

## Validation

LOCAL_CI_FAST=PASS

LOCAL_CI=PASS

TESTS=35_BACKEND_92_PERCENT_COVERAGE_8_ADMIN_5_MOBILE_3_GOVERNANCE

DOCKER=PASS_ISOLATED_DWCO_CI_NO_REMAINING_CONTAINERS_OR_VOLUMES

CONTROL_PLANE=HEALTH_AND_API_200_BEFORE_AND_AFTER_FULL_CI

REVIEWS=ARCHITECTURE_PASS_IDENTITY_SECURITY_PASS_QA_VALIDATION_PASS_DEVOPS_SRE_PASS_WITH_EXCEPTIONS

## Remaining gaps

- DEP-001: remote GitHub Actions attestation and required branch protection remain unavailable.
- Realtime fan-out remains process-local and needs a broker/scalable revocation design before any
  shared or horizontal environment.
- The Redis mutation limiter remains fail-open and is not approved for shared/production use.
- Production capacity, backup/restore, rollback, SLO/alerting, and operations evidence do not exist.
- The 1,000-message reconnect cap is explicit; a later product decision may refine recovery UX.
- PSTN/SIP/PBX, WebRTC media, eSIM, AI, billing, and production deployment remain unstarted or
  unauthorized.

## Recommended next approval gate

Merge the documentation-only status reconciliation without deploying it. The next active gate is
DWCO 0.5 contract approval; app-to-app voice/WebRTC implementation may begin only after that separate
contract passes Architecture, Identity/Security, QA/Validation, DevOps/SRE, and Implementation
Director approval.
