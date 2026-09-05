# DWCO 0.5 evidence manifest template

MANIFEST_STATUS=TEMPLATE_NOT_EXECUTED

IMPLEMENTATION_AUTHORIZED=NO

Complete this file or an equivalent machine-readable manifest against the immutable implementation
commit. Generated raw artifacts remain outside Git; commit only sanitized summaries and hashes.

```text
CONTRACT_COMMIT=
IMPLEMENTATION_COMMIT=
SOURCE_BRANCH=
ENVIRONMENT=ISOLATED_LOCAL_ONLY
STARTED_AT=
COMPLETED_AT=
OPERATOR=
REMOTE_CI_STATUS=
LOCAL_FAST_STATUS=
LOCAL_FULL_STATUS=
DOCKER_ISOLATION_STATUS=
MIGRATION_ROUNDTRIP_STATUS=
DEPENDENCY_LICENSE_STATUS=
DEPENDENCY_IMAGE_SCAN_STATUS=
ANDROID_MANIFEST_ALLOWLIST_STATUS=
IOS_INFO_ENTITLEMENT_ALLOWLIST_STATUS=
SECRET_SCAN_STATUS=
GOVERNANCE_HEALTH_BEFORE=
GOVERNANCE_HEALTH_AFTER=
DEPLOYMENT_STATUS=NOT_AUTHORIZED_NOT_DEPLOYED
```

| Evidence ID | QA/V IDs | Sanitized artifact type | Required fields |
|---|---|---|---|
| E-STATE | QA-03 to QA-05; V03 to V09 | JUnit/JSON transition report | command, prior/result state, version, race result, pass/fail |
| E-AUTH | QA-09 to QA-10; V10 to V14 | JUnit/JSON denial matrix | scenario ID, non-sensitive status/event count, timing, pass/fail |
| E-SIGNAL | QA-06; V08, V09, V18, V19, V24, V25 | JUnit/JSON signaling report | counts, revisions, gap outcome, bounds; no bodies/candidates |
| E-MEDIA | QA-07; V01, V02, V20 to V23, V26 | JSON peer/network report | platform, transport enum, setup/recovery timing, DTLS-SRTP assertion, quality bucket |
| E-MOBILE | QA-08; V15 to V18, V27 | Prebuild diff/hash plus JUnit/device summary | platform/OS/build hash, generated permission/feature/service/provider/usage-description allowlist result, lifecycle state, resource cleanup; no device label/token |
| E-PRIVACY | QA-11; V28, V29 | Redaction inspection checklist | inspected DB/log/trace/audit/crash/mobile surfaces and zero prohibited matches |
| E-LOAD | QA-12, QA-14; V24, V25, V30, V31 | JSON capacity/telemetry report | attempts, success/rejection, p50/p95, enum route, aggregate resources |
| E-ROLLBACK | QA-15; V32 | Shell/JUnit summary | kill switch, drain, purge, scoped Docker cleanup, 0.1-0.4 and health results |
| E-REGRESSION | QA-02, QA-13 | JUnit/build/audit summary | exact commands, exit codes, counts, coverage, migration heads |
| E-REVIEW | QA-01, QA-16 | Markdown decisions | reviewer, independence, exact SHA, decision, exceptions, timestamp |

For each artifact record relative location, SHA-256, producing command/test name, start/end time,
approved platform/runtime identifiers, pass/fail, redaction reviewer, and linked defect. Packet-level
proof may report protocol and relay transport only; packet captures, SDP, candidates, IPs, secrets,
tokens, audio, and raw device logs are never committed.
