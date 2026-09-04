# DWCO 0.4 acceptance remediation review record

REVIEW_STATUS=REMEDIATION_IMPLEMENTED_REVIEW_PENDING

BASELINE=MAIN_19680CD

ACCEPTED_WEIGHTED_COMPLETION=UNCHANGED_AT_34_PERCENT_APPROXIMATE

DEPLOYMENT_STATUS=NOT_AUTHORIZED_NOT_DEPLOYED

## Initial independent findings

| Reviewer | Initial result | Finding | Required closure |
|---|---|---|---|
| Architecture | Fail / High | Request-scoped SQLAlchemy session remained open for the WebSocket lifetime | Close the session before acceptance and prove bounded-pool isolation |
| Identity/Security | Fail / High | Established sockets cached membership and permissions after revocation | Revalidate before subsequent fan-out and disconnect inactive contexts |
| QA/Validation | Fail / Major | Mobile reconnect obtained a new ticket but did not run required HTTP catch-up | Catch up the open conversation and add lifecycle-oriented regression tests |
| DevOps/SRE | Pass with external exceptions | Local gates are usable; GitHub Actions and branch protection remain unresolved | Preserve no-deployment boundary and DEP-001 status |

## Implemented remediation evidence

| Area | Evidence | Status |
|---|---|---|
| Database lifetime | `authorize_realtime_claims` uses a short session before socket acceptance; bounded QueuePool test checks zero retained connections | Implemented; re-review pending |
| Runtime revocation | Hub refreshes authorization before user/tenant fan-out, disconnects inactive membership, refreshes permission filters, and contains authorization-store failure per connection | Implemented; re-review pending |
| Mobile reconnect | `realtime.ready` triggers authenticated, paginated `after_sequence` HTTP history for the open conversation; reconciliation deduplicates/sorts, retries once per page, and fails visibly at a 1,000-message safety cap | Implemented; re-review pending |
| Automated checks | 35 backend tests at 92% coverage, 8 admin tests/build, 5 mobile gap/pagination/retry/reconciliation tests, dependency audits, migration round-trip, Docker build/readiness, governance tests, workflow/repository checks, isolated CI cleanup, and live governance pre/post health | Final revalidation pending |

## Residual boundaries

- The hub remains intentionally process-local; horizontal/shared service requires an approved broker.
- The Redis mutation limiter remains fail-open and is not approved for shared or production use.
- DEP-001 remains open: GitHub Actions remote attestation and required branch protection are absent.
- The direct-participant count invariant remains application-enforced; a database-level invariant is
  a later hardening decision.
- No production deployment or DWCO 0.5 capability is authorized.

## Acceptance rule

This branch cannot change accepted stage weight. DWCO 0.4 remains at 0% accepted contribution until
the remediation is merged, all required reviewers record acceptance, and the canonical status is
reconciled from merged evidence. Only then may overall accepted completion move from approximately
34% to 48%.
