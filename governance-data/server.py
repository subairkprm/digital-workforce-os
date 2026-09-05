from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

DEFAULT_EVIDENCE_ROOT = Path("/evidence")
DEFAULT_LOCAL_CI_RECEIPT = Path("/local-ci/latest.json")
MAX_LOCAL_CI_RECEIPT_BYTES = 16 * 1024
EVIDENCE_FILES = {
    "project_status": Path("PROJECT_STATUS.md"),
    "master_plan": Path("MASTER_PROJECT_PLAN.md"),
    "dependencies": Path("DEPENDENCY_REGISTER.md"),
}


def read_evidence(root: Path) -> dict[str, str]:
    resolved_root = root.resolve()
    documents: dict[str, str] = {}
    for name, relative_path in EVIDENCE_FILES.items():
        path = (resolved_root / relative_path).resolve()
        if resolved_root not in path.parents:
            raise ValueError(f"Evidence path escapes root: {relative_path}")
        documents[name] = path.read_text(encoding="utf-8")
    project = parse_assignments(documents["project_status"])
    gate = project.get("CURRENT_GATE", "")
    review_name = f"{gate.replace('_', '-')}.md"
    if not re.fullmatch(r"[A-Z0-9.-]+\.md", review_name):
        raise ValueError("Current review name is not safe")
    review_path = (resolved_root / "reviews" / review_name).resolve()
    if resolved_root not in review_path.parents:
        raise ValueError("Current review path escapes root")
    documents["acceptance_review"] = review_path.read_text(encoding="utf-8")
    documents["acceptance_review_name"] = review_name
    return documents


def parse_assignments(markdown: str) -> dict[str, str]:
    return {
        match.group(1): match.group(2).strip()
        for match in re.finditer(r"^([A-Z][A-Z0-9_]*)=(.+)$", markdown, re.MULTILINE)
    }


def section(markdown: str, heading: str) -> str:
    match = re.search(
        rf"^##\s+{re.escape(heading)}\s*$\n(?P<body>.*?)(?=^##\s+|\Z)",
        markdown,
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    return match.group("body").strip() if match else ""


def parse_table(markdown_section: str) -> list[dict[str, str]]:
    rows = [
        line.strip()
        for line in markdown_section.splitlines()
        if line.strip().startswith("|")
    ]
    if len(rows) < 2:
        return []
    headers = [cell.strip() for cell in rows[0].strip("|").split("|")]
    records: list[dict[str, str]] = []
    for row in rows[2:]:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) != len(headers):
            continue
        records.append(dict(zip(headers, cells)))
    return records


def parse_bullets(markdown_section: str) -> list[str]:
    bullets: list[str] = []
    current: list[str] = []
    for line in markdown_section.splitlines():
        item = re.match(r"^-\s+(.+)$", line)
        if item:
            if current:
                bullets.append(" ".join(current))
            current = [item.group(1).strip()]
        elif current and line.strip() and not line.startswith(("#", "|")):
            current.append(line.strip())
        elif current and not line.strip():
            bullets.append(" ".join(current))
            current = []
    if current:
        bullets.append(" ".join(current))
    return bullets


def first_number(value: str, default: int = 0) -> int:
    match = re.search(r"\d+", value)
    return int(match.group()) if match else default


def stage_state(status: str) -> str:
    normalized = status.casefold()
    if normalized == "complete":
        return "accepted"
    if "implemented" in normalized:
        return "review"
    return "future"


def review_is_open(result: str) -> bool:
    normalized = result.casefold()
    return any(
        term in normalized for term in ("open", "pending", "fail", "in progress")
    )


def classify_exception(risk: str) -> tuple[str, str, str]:
    normalized = risk.casefold()
    if any(term in normalized for term in ("github", "remote ci", "protected")):
        return "high", "DevOps / SRE", "Remote CI and branch protection"
    if any(term in normalized for term in ("limiter", "fail-open", "redis outage")):
        return "high", "Identity / Security", "Redis failure policy"
    if any(term in normalized for term in ("hub", "horizontally scaled", "broker")):
        return "medium", "Architecture + Realtime", "Realtime scale boundary"
    if any(term in normalized for term in ("push-provider", "pstn", "esim")):
        return (
            "medium",
            "Integration + Provider agents",
            "Deferred provider capabilities",
        )
    return "medium", "Implementation Director", "Open evidence exception"


def unavailable_local_ci(result: str, note: str) -> dict[str, Any]:
    return {
        "schemaVersion": 1,
        "result": result,
        "sourceCommit": None,
        "sourceBranch": None,
        "startedAt": None,
        "completedAt": None,
        "durationSeconds": None,
        "gateExitCode": None,
        "workflowSha256": None,
        "gateScriptSha256": None,
        "worktreeClean": None,
        "scope": "TRUSTED_LOCAL_MACHINE_ONLY",
        "remoteCiStatus": "UNAVAILABLE_NOT_ATTESTED",
        "deploymentStatus": "NOT_AUTHORIZED_NOT_DEPLOYED",
        "note": note,
        "runner": {},
    }


def load_local_ci_receipt(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return unavailable_local_ci("NOT_RUN", "No local CI receipt is available.")
    try:
        if path.stat().st_size > MAX_LOCAL_CI_RECEIPT_BYTES:
            raise ValueError("Receipt is too large")
        receipt = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(receipt, dict):
            raise ValueError("Receipt must be an object")
        required_exact = {
            "scope": "TRUSTED_LOCAL_MACHINE_ONLY",
            "remoteCiStatus": "UNAVAILABLE_NOT_ATTESTED",
            "deploymentStatus": "NOT_AUTHORIZED_NOT_DEPLOYED",
        }
        if receipt.get("schemaVersion") != 1:
            raise ValueError("Unsupported receipt schema")
        if receipt.get("result") not in {"PASS", "FAIL"}:
            raise ValueError("Invalid result")
        if any(receipt.get(key) != value for key, value in required_exact.items()):
            raise ValueError("Invalid receipt boundary")
        for field in ("sourceCommit", "finalCommit"):
            if not re.fullmatch(r"[0-9a-f]{40}", str(receipt.get(field, ""))):
                raise ValueError(f"Invalid {field}")
        for field in ("workflowSha256", "gateScriptSha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", str(receipt.get(field, ""))):
                raise ValueError(f"Invalid {field}")
        if not isinstance(receipt.get("worktreeClean"), bool):
            raise ValueError("Invalid worktreeClean")
        for field in ("durationSeconds", "gateExitCode"):
            if not isinstance(receipt.get(field), int) or receipt[field] < 0:
                raise ValueError(f"Invalid {field}")
        runner = receipt.get("runner")
        if not isinstance(runner, dict):
            raise ValueError("Invalid runner")
        bounded_fields = (
            "sourceBranch",
            "startedAt",
            "completedAt",
            "note",
        )
        if any(
            not isinstance(receipt.get(field), str) or len(receipt[field]) > 256
            for field in bounded_fields
        ):
            raise ValueError("Invalid receipt text")
        allowed_runner = {"os", "arch", "python", "node", "pnpm", "docker"}
        if set(runner) - allowed_runner or any(
            not isinstance(value, str) or len(value) > 128 for value in runner.values()
        ):
            raise ValueError("Invalid runner values")
        return {
            key: receipt[key]
            for key in (
                "schemaVersion",
                "result",
                "sourceCommit",
                "sourceBranch",
                "startedAt",
                "completedAt",
                "durationSeconds",
                "gateExitCode",
                "workflowSha256",
                "gateScriptSha256",
                "worktreeClean",
                "scope",
                "remoteCiStatus",
                "deploymentStatus",
                "note",
                "runner",
            )
        }
    except (OSError, ValueError, json.JSONDecodeError, KeyError, TypeError):
        return unavailable_local_ci(
            "INVALID", "The local CI receipt is malformed or outside its trust boundary."
        )


def build_snapshot(root: Path, local_ci_receipt: Path | None = None) -> dict[str, Any]:
    documents = read_evidence(root)
    local_ci = load_local_ci_receipt(local_ci_receipt)
    project = parse_assignments(documents["project_status"])
    review = parse_assignments(documents["acceptance_review"])
    stages = parse_table(section(documents["master_plan"], "Stage map and weight"))
    dependencies = parse_table(
        section(documents["dependencies"], "Dependency register")
    )
    if not dependencies:
        dependencies = parse_table(documents["dependencies"])
    gates = parse_table(section(documents["acceptance_review"], "Acceptance evidence"))

    stage_records = []
    implemented_completion = 0
    for stage in stages:
        if "total" in stage.get("Stage", "").casefold():
            continue
        status = stage.get("Canonical status", "Unknown")
        weight = first_number(stage.get("Weight", "0"))
        state = stage_state(status)
        if state in {"accepted", "review"}:
            implemented_completion += weight
        stage_records.append(
            {
                "stage": stage.get("Stage", "Unknown"),
                "capability": stage.get("Product boundary", "Unknown"),
                "weight": weight,
                "status": status,
                "state": state,
            }
        )

    open_reviews = [gate for gate in gates if review_is_open(gate.get("Result", ""))]
    residual_risks = parse_bullets(
        section(documents["acceptance_review"], "Review findings")
    )
    blocking_dependencies = [
        item
        for item in dependencies
        if any(
            term in item.get("State", "").casefold()
            for term in ("blocked", "pending", "deferred")
        )
    ]
    digest_input = "\n".join(documents[name] for name in sorted(documents))
    digest_input += "\n" + json.dumps(local_ci, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()[:12]

    return {
        "meta": {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "contentDigest": digest,
            "refreshSeconds": 15,
            "sourceOfTruth": project.get("SOURCE_OF_TRUTH", "Unavailable"),
            "statusAsOf": project.get("STATUS_AS_OF", "Unavailable"),
            "currentGate": project.get("CURRENT_GATE", "Unavailable").replace("_", " "),
            "deploymentStatus": project.get("DEPLOYMENT_STATUS", "Unavailable").replace(
                "_", " "
            ),
            "reviewStatus": review.get("REVIEW_STATUS", "Unavailable").replace(
                "_", " "
            ),
            "reviewSource": documents["acceptance_review_name"],
        },
        "metrics": {
            "acceptedCompletion": first_number(
                project.get("ACCEPTED_WEIGHTED_COMPLETION", "0")
            ),
            "implementedCompletion": implemented_completion,
            "openReviews": len(open_reviews),
            "activeExceptions": len(residual_risks),
        },
        "stages": stage_records,
        "qualityGates": gates,
        "openReviews": open_reviews,
        "dependencies": dependencies,
        "exceptions": [
            {
                "severity": classification[0],
                "owner": classification[1],
                "title": classification[2],
                "summary": risk,
            }
            for risk in residual_risks
            for classification in [classify_exception(risk)]
        ],
        "verification": parse_bullets(
            section(documents["project_status"], "Verification status")
        ),
        "blockingDependencies": blocking_dependencies,
        "localCi": local_ci,
    }


class GovernanceHandler(BaseHTTPRequestHandler):
    server_version = "DWCOGovernanceData/0.2"

    def send_json(
        self,
        status: HTTPStatus,
        payload: dict[str, Any],
        etag: str | None = None,
        include_body: bool = True,
    ) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        if etag:
            self.send_header("ETag", f'"{etag}"')
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def do_HEAD(self) -> None:
        if self.path == "/healthz":
            self.send_json(HTTPStatus.OK, {"status": "healthy"}, include_body=False)
            return
        if self.path == "/api/governance":
            try:
                snapshot = build_snapshot(  # type: ignore[attr-defined]
                    self.server.evidence_root, self.server.local_ci_receipt
                )
            except (OSError, ValueError):
                self.send_json(
                    HTTPStatus.SERVICE_UNAVAILABLE,
                    {"error": "evidence_unavailable"},
                    include_body=False,
                )
                return
            self.send_json(
                HTTPStatus.OK,
                snapshot,
                snapshot["meta"]["contentDigest"],
                include_body=False,
            )
            return
        self.send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"}, include_body=False)

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self.send_json(HTTPStatus.OK, {"status": "healthy"})
            return
        if self.path != "/api/governance":
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        try:
            snapshot = build_snapshot(  # type: ignore[attr-defined]
                self.server.evidence_root, self.server.local_ci_receipt
            )
        except (OSError, ValueError) as error:
            self.log_error("Evidence snapshot failed: %s", type(error).__name__)
            self.send_json(
                HTTPStatus.SERVICE_UNAVAILABLE, {"error": "evidence_unavailable"}
            )
            return
        self.send_json(HTTPStatus.OK, snapshot, snapshot["meta"]["contentDigest"])


class GovernanceServer(ThreadingHTTPServer):
    def __init__(
        self,
        address: tuple[str, int],
        evidence_root: Path,
        local_ci_receipt: Path | None = None,
    ):
        self.evidence_root = evidence_root
        self.local_ci_receipt = local_ci_receipt
        super().__init__(address, GovernanceHandler)


def main() -> None:
    root = Path(os.environ.get("DWCO_GOVERNANCE_EVIDENCE_ROOT", DEFAULT_EVIDENCE_ROOT))
    local_ci_receipt = Path(
        os.environ.get("DWCO_LOCAL_CI_RECEIPT", DEFAULT_LOCAL_CI_RECEIPT)
    )
    port = int(os.environ.get("DWCO_GOVERNANCE_DATA_PORT", "8081"))
    GovernanceServer(("0.0.0.0", port), root, local_ci_receipt).serve_forever()


if __name__ == "__main__":
    main()
