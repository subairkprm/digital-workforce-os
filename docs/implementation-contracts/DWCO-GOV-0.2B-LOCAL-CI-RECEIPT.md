# DWCO-GOV 0.2B — Local CI exact-commit receipt contract

CONTRACT_STATUS=APPROVED_BY_USER_FOR_BOUNDED_LOCAL_IMPLEMENTATION

## Objective

Provide a safe local substitute for unavailable GitHub Actions execution by enforcing the complete
existing gate, recording exact-commit evidence, and exposing only a sanitized read-only result in the
governance control plane. Preserve all application and production behavior.

## In scope

- Clean-tree, exact-commit, atomic JSON receipts for complete local CI results.
- Failure and interruption receipts; gate and workflow file hashes; bounded runner metadata.
- Pre-push enforcement with exact-commit cache validation.
- Read-only, size-limited, schema-validated receipt ingestion and dashboard rendering.
- Static HTML structure checks, governance unit tests, repository baseline validation, and a documented
  parity matrix.

## Excluded and prohibited

- Claiming GitHub-hosted or independent attestation.
- Deployment, production access, branch protection changes, merge, approval, or stage-credit changes.
- GitHub tokens, secrets, environment dumps, customer data, usernames, IP addresses, or arbitrary
  receipt fields.
- Legal, licensing, privacy, telecom, eSIM, billing, or regulatory approval.

## Acceptance criteria

- A dirty tree is refused, a failed or interrupted gate writes `FAIL`, and a clean unchanged commit can
  write `PASS` only after every complete gate step succeeds.
- Receipt JSON is ignored by Git and mounted read-only into the governance evidence service.
- Missing and malformed receipts are displayed as `NOT RUN` and `INVALID` respectively without
  breaking canonical project evidence.
- The dashboard has unique element IDs, balanced explicit tags, matching views/tabs, and live receipt
  fields.
- Existing backend, database, admin, mobile, messaging, and production behavior is unchanged.

DEPLOYMENT_STATUS=LOCAL_ONLY_NOT_AUTHORIZED_FOR_PRODUCTION
