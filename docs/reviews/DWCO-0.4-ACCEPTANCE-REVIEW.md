# DWCO 0.4 acceptance review

REVIEW_STATUS=REMEDIATION_SIGN_OFFS_COMPLETE_MERGE_PENDING

MERGED_EVIDENCE=PR_21_MAIN_D965126

TECHNICAL_VALIDATION=PASS_LOCAL_REMEDIATION_97E3664

REMOTE_CI=UNRESOLVED_NO_USABLE_GITHUB_ATTESTATION

STAGE_CREDIT=UNCHANGED_AT_34_PERCENT_OVERALL

DEPLOYMENT_STATUS=NOT_AUTHORIZED_NOT_DEPLOYED

## Acceptance evidence

| Gate | Result | Evidence or remaining action |
|---|---|---|
| Approved bounded contract | Pass | `docs/implementation-contracts/DWCO-0.4-REALTIME-COMMUNICATION-CONTRACT.md` |
| Implementation and migration merged | Pass | PR #21; merge commit `d965126`; migration `0005_realtime_messaging` |
| Local tests, builds, audits, migration, and Docker checks | Pass | `docs/completion-reports/DWCO-0.4-REALTIME-COMMUNICATION.md` |
| Completion report and rollback boundary | Pass | Completion report records gaps, rollback, and no-deployment state |
| Independent QA/Validation review | Pass | Paginated reconnect gap/retry/cap behavior and exact-tree local evidence accepted |
| Architecture review | Pass | Short DB authorization lifetime, bounded HTTP catch-up, and failure containment accepted |
| Identity/Security review | Pass | Runtime revocation, permission refresh, and fail-closed store-failure behavior accepted |
| DevOps/SRE review | Pass with external exceptions | Isolated CI and live-control-plane coexistence accepted; DEP-001 remains |
| Project status reconciliation | Pending merge | Accepted weight remains 34% until this exact remediation is merged |

## Review findings

Independent review identified two High findings and one Major finding in the merged implementation:
database sessions remained open for WebSocket lifetime, established sockets retained stale
authorization until disconnect, and mobile reconnect did not perform the contract-required HTTP
history catch-up. A bounded remediation is implemented under
`docs/implementation-contracts/DWCO-0.4-ACCEPTANCE-REMEDIATION.md`. All four required review roles
now accept the bounded remediation, with DevOps/SRE external exceptions. The stage remains
**Implemented, pending acceptance** until the reviewed commits are merged and canonical status is
reconciled.

Residual risks are explicit:

- `main` is not protected and DEP-001 still blocks required remote checks.
- The realtime live hub is process-local; shared or horizontally scaled operation requires an
  approved broker and environment design.
- The inherited mutation limiter is fail-open during Redis outage and needs a production policy
  decision before shared or production operation.
- Push-provider delivery, production abuse operations, WebRTC voice, PSTN, eSIM, billing, AI, and
  production deployment remain outside this stage.

## Closure actions

1. Review and merge the exact approved remediation commits; do not squash away the evidence binding
   without updating this record.
2. Keep the DevOps/SRE external exceptions and no-deployment boundary visible.
3. Reconcile `PROJECT_STATUS.md` and `docs/roadmap/COMPLETION_MODEL.md` to 48% only after all required
   acceptance evidence is recorded.
4. Keep DWCO-009 open until GitHub Actions runs successfully and required branch protection is
   enabled.

## Next-stage boundary

After DWCO 0.4 acceptance, draft and review a separate DWCO 0.5 app-to-app voice/WebRTC contract.
That future contract must resolve media security, consent, TURN/coturn, network-failure testing,
observability, abuse controls, and rollback. It must not authorize PSTN/SIP/PBX, recording, carrier
or eSIM work, AI, billing, or production deployment.
