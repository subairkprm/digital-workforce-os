# DWCO-GOV 0.2A local live evidence completion report

CONTRACT_ID=DWCO-GOV-0.2A-LOCAL-LIVE-EVIDENCE

FILES_CHANGED=Governance evidence parser/API and tests, live dashboard renderer, isolated Docker
sidecar/network, configurable development/CI ports, safe pre-push Docker project, roadmap, README,
contract, and this report

APPLICATION_CHANGES=NONE; no backend, tenant admin, mobile, database, migration, Redis, identity,
messaging, realtime, or production behavior changed

DATA_FLOW=Browser polls same-origin `/api/governance`; nginx proxies to an internal-only evidence
service; the service reads four whitelisted, read-only repository documents and returns normalized
JSON with a content digest

SECURITY_CHANGES=Internal governance data network plus separate nginx ingress network; unprivileged
read-only evidence container with no published port or external network; no secrets, GitHub token,
database, Redis, application API, customer data,
arbitrary file endpoint, rendered repository HTML, or mutating controls

TEST_RESULTS=Three parser, digest, HTTP, and HEAD tests PASS; JavaScript syntax PASS; live document digest changed
without rebuild and returned after rollback; Compose configuration and both governance images PASS;
HTTP/API/HEAD, content-digest, security-header, stage/quality/deviation rendering, internal-network and
unpublished-data-port checks PASS; full local CI PASS with 31 backend tests at 92% coverage, 8 admin
tests/build, mobile checks, audits, migrations, PostgreSQL/Redis readiness, and isolated CI cleanup;
the port-3100 dashboard remained HTTP 200 after cleanup

KNOWN_GAPS=GitHub PR/check status is not live; repository documents must still be updated through the
reviewed Git workflow; browser accessibility/device review and authenticated reviewer workflow
remain pending

DEFERRED_SCOPE=GitHub credential adapter, signed webhooks, persistence, authentication/RBAC,
immutable signatures, approvals, waivers, deployments, and production hosting

DEPLOYMENT_STATUS=LOCAL_DOCKER_ONLY_NOT_AUTHORIZED_FOR_PRODUCTION

ROLLBACK_GUIDANCE=Stop governance-web and governance-data, then revert the GOV 0.2A commits. The
product application and database require no rollback.
