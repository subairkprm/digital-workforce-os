import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

from server import GovernanceServer, build_snapshot

PROJECT_STATUS = """\
STATUS_AS_OF=2026-09-04
SOURCE_OF_TRUTH=merged main at abc1234
ACCEPTED_WEIGHTED_COMPLETION=34_PERCENT_APPROXIMATE
CURRENT_GATE=DWCO_0.4_ACCEPTANCE_REVIEW
DEPLOYMENT_STATUS=NOT_AUTHORIZED_NOT_DEPLOYED

## Verification status

- Local gates passed.
- Remote CI remains unresolved.
"""

MASTER_PLAN = """\
## Stage map and weight

| Stage | Product boundary | Weight | Canonical status |
|---|---|---:|---|
| DWCO 0.1 | Foundation | 12% | Complete |
| DWCO 0.4 | Realtime | 14% | Implemented and merged; acceptance review pending |
| DWCO 0.5 | Voice | 12% | Not started |
"""

DEPENDENCIES = """\
# Dependency register

| ID | Dependency | State | Impact | Owner | Exit evidence |
|---|---|---|---|---|---|
| DEP-001 | Remote CI | Blocked externally | No attestation | DevOps/SRE | Passing checks |
"""

REVIEW = """\
REVIEW_STATUS=PENDING_REQUIRED_SIGN_OFFS

## Acceptance evidence

| Gate | Result | Evidence or remaining action |
|---|---|---|
| Local tests | Pass | Report |
| QA review | Open | Independent validation |
| Security review | Fail; remediation pending | Re-review required |
| Status reconciliation | In progress | Merge required |

## Review findings

Residual risks are explicit:

- Remote CI is unavailable.
- Realtime hub is process-local.
"""


class SnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        (self.root / "reviews").mkdir()
        (self.root / "PROJECT_STATUS.md").write_text(PROJECT_STATUS, encoding="utf-8")
        (self.root / "MASTER_PROJECT_PLAN.md").write_text(MASTER_PLAN, encoding="utf-8")
        (self.root / "DEPENDENCY_REGISTER.md").write_text(
            DEPENDENCIES, encoding="utf-8"
        )
        (self.root / "reviews/DWCO-0.4-ACCEPTANCE-REVIEW.md").write_text(
            REVIEW, encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def test_snapshot_derives_live_metrics_and_gates(self) -> None:
        snapshot = build_snapshot(self.root)

        self.assertEqual(snapshot["metrics"]["acceptedCompletion"], 34)
        self.assertEqual(snapshot["metrics"]["implementedCompletion"], 26)
        self.assertEqual(snapshot["metrics"]["openReviews"], 3)
        self.assertEqual(len(snapshot["openReviews"]), 3)
        self.assertEqual(snapshot["metrics"]["activeExceptions"], 2)
        self.assertEqual(snapshot["stages"][1]["state"], "review")
        self.assertEqual(snapshot["blockingDependencies"][0]["ID"], "DEP-001")
        self.assertEqual(len(snapshot["stages"]), 3)
        self.assertEqual(
            snapshot["exceptions"][0]["summary"], "Remote CI is unavailable."
        )
        self.assertEqual(snapshot["exceptions"][0]["owner"], "DevOps / SRE")

    def test_digest_changes_when_evidence_changes(self) -> None:
        first = build_snapshot(self.root)["meta"]["contentDigest"]
        (self.root / "PROJECT_STATUS.md").write_text(
            PROJECT_STATUS.replace("34_PERCENT", "35_PERCENT"), encoding="utf-8"
        )
        second = build_snapshot(self.root)["meta"]["contentDigest"]

        self.assertNotEqual(first, second)

    def test_http_api_and_head_are_read_only_and_uncached(self) -> None:
        server = GovernanceServer(("127.0.0.1", 0), self.root)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base_url = f"http://127.0.0.1:{server.server_port}"
            with urlopen(f"{base_url}/api/governance", timeout=2) as response:
                payload = json.load(response)
                self.assertEqual(response.headers["Cache-Control"], "no-store")
                self.assertEqual(payload["metrics"]["acceptedCompletion"], 34)
            request = Request(f"{base_url}/api/governance", method="HEAD")
            with urlopen(request, timeout=2) as response:
                self.assertEqual(response.status, 200)
                self.assertTrue(response.headers["ETag"])
                self.assertEqual(response.read(), b"")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
