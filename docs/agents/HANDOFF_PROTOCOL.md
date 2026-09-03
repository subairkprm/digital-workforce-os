# Agent handoff protocol

## Required fields

```text
HANDOFF_ID=
CONTRACT_ID=
STAGE=
SOURCE_BRANCH=
SOURCE_COMMIT=
FROM_AGENT=
TO_AGENT=
OBJECTIVE=
IN_SCOPE=
OUT_OF_SCOPE=
FILES_CHANGED=
DATABASE_CHANGES=
API_CHANGES=
SECURITY_AND_PRIVACY_CHANGES=
DEPENDENCIES_AND_ASSUMPTIONS=
TESTS_RUN=
TEST_RESULTS=
REMOTE_CI_STATUS=
LOCAL_CI_STATUS=
KNOWN_ISSUES=
DEFERRED_SCOPE=
DEPLOYMENT_STATUS=
ROLLBACK_GUIDANCE=
REVIEWERS_REQUIRED=
OPEN_DECISIONS=
NEXT_ACTION=
```

## Procedure

1. Sender verifies contract scope and records exact source evidence.
2. Receiver checks commit, scope, migration order, API/security effects, tests, and gaps.
3. Missing or contradictory fields return to the sender; silence is not acceptance.
4. Reviewers record approval, changes, or a named blocker against acceptance criteria.
5. QA/Validation reconciles evidence with the contract and completion model.
6. Implementation Director accepts the handoff or assigns a bounded follow-up.

Never hand off secrets or production data; describe local CI as remote CI; omit failed checks,
rollback risk, or deferred work; expand scope; or authorize deployment through a handoff.
