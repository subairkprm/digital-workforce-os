# Completion model

## Purpose and formula

Report durable product progress without treating code volume, an open PR, or locally passing tests
as accepted completion: `overall completion = sum(stage weight x accepted fraction)`.

The current model uses binary stage acceptance. Partial capabilities are reported separately and
earn no stage weight until the stage gate closes. Reweighting requires an approved master-plan
change and must not be used to manufacture progress.

| Stage | Weight | Accepted | Contribution |
|---|---:|---:|---:|
| DWCO 0.1 | 12% | 100% | 12% |
| DWCO 0.2 | 10% | 100% | 10% |
| DWCO 0.3 | 12% | 100% | 12% |
| DWCO 0.4 | 14% | 0% | 0% |
| DWCO 0.5 | 12% | 0% | 0% |
| DWCO 0.6 | 12% | 0% | 0% |
| DWCO 0.7 | 8% | 0% | 0% |
| DWCO 0.8 | 7% | 0% | 0% |
| DWCO 0.9 | 6% | 0% | 0% |
| DWCO 1.0 | 7% | 0% | 0% |
| **Total** | **100%** |  | **34%** |

The merged DWCO 0.4 presence capability is prerequisite evidence. It does not mean the realtime
communication stage—including transport, messaging, retention, mobile delivery, and operations—is
accepted.

## Stage acceptance gate

A stage is accepted only when all are true:

1. An approved contract defines scope, exclusions, invariants, owners, reviewers, and rollback.
2. Implementation and migrations are merged to `main`.
3. Required tests, builds, security checks, and dependency audits pass.
4. QA/Validation independently checks acceptance criteria and regression evidence.
5. Architecture and Identity/Security accept material boundary changes.
6. A completion report identifies remaining gaps and deployment status.
7. `PROJECT_STATUS.md` is reconciled with the merged evidence.

Remote CI is the required authority. While DEP-001 is open, local fallback evidence must state that
remote CI is unresolved and may not claim remote verification.

## Status vocabulary

- **Not started:** no approved active contract and no accepted delivery.
- **Draft:** proposed contract, not authorized.
- **Planned:** next boundary awaiting approval or execution.
- **In progress:** approved contract under implementation.
- **Implemented, pending acceptance:** code exists but acceptance conditions remain.
- **Complete:** accepted under this model.
- **Blocked:** a named dependency has no safe in-scope workaround.
