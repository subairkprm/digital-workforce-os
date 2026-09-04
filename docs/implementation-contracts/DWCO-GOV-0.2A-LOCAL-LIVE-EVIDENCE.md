# DWCO-GOV 0.2A — Local live evidence ingestion contract

CONTRACT_STATUS=APPROVED_BY_USER_FOR_BOUNDED_LOCAL_IMPLEMENTATION

## Objective

Replace representative dashboard values with an automatically refreshed, read-only view derived
from canonical repository documents in the current local checkout. Preserve the governance plane's
separation from application data and operational controls.

## In scope

- A local read-only evidence service with no third-party dependencies.
- Whitelisted ingestion of `PROJECT_STATUS.md`, `MASTER_PROJECT_PLAN.md`,
  `DEPENDENCY_REGISTER.md`, and the DWCO 0.4 acceptance review.
- Derived accepted/implemented progress, stage state, quality gates, open reviews, dependencies,
  and recorded exceptions.
- Browser polling every 15 seconds, manual refresh, content digest, and stale/error indication.
- A private internal Docker data network shared only by the governance UI and evidence service,
  plus a separate browser-ingress network for the static UI.
- Parser, digest-change, JavaScript, Compose, HTTP, security-header, and isolation validation.

## Security boundaries

- No GitHub credential, API, webhook, database, Redis, application API, customer data, or production
  connection.
- Repository evidence is mounted read-only; the service can open only the four configured sources.
- The evidence service has no published host port or external/application network path; only nginx
  joins the browser-ingress network.
- The browser receives normalized fields, not arbitrary file access or rendered Markdown/HTML.
- No merge, approval, waiver, stage-credit, deployment, or document mutation control.
- Missing or malformed evidence fails closed as unavailable and retains the last browser snapshot.

## Explicitly deferred

- GitHub PR/check synchronization, which requires a separate minimal-scope credential and threat
  review.
- Signed webhook ingestion, persistent records, authentication, RBAC, reviewer signatures, and
  immutable audit history.
- Customer or production hosting and every product-stage capability.

## Acceptance criteria

- Changing a whitelisted source changes the content digest and dashboard data without rebuilding.
- Accepted completion remains sourced from `PROJECT_STATUS.md`; implemented weight is derived from
  the weighted master stage map and never converted into accepted stage credit.
- The static fallback remains usable when the evidence service is unavailable.
- Governance containers remain unprivileged, read-only, externally disconnected, and isolated from
  the application Docker network.
- Existing API, database, Redis, admin, and mobile behavior remains unchanged.

DEPLOYMENT_STATUS=LOCAL_ONLY_NOT_AUTHORIZED_FOR_PRODUCTION
