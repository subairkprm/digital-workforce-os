import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ZERO_SHA = "0" * 40


class PrePushHookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)
        (self.root / ".githooks").mkdir()
        (self.root / ".github/workflows").mkdir(parents=True)
        (self.root / ".local-ci").mkdir()
        (self.root / "scripts").mkdir()
        shutil.copy2(
            REPOSITORY_ROOT / ".githooks/pre-push", self.root / ".githooks/pre-push"
        )
        (self.root / ".github/workflows/ci.yml").write_text(
            "name: test\n", encoding="utf-8"
        )
        (self.root / "scripts/ci-local.sh").write_text(
            "#!/bin/sh\nexit 0\n", encoding="utf-8"
        )
        (self.root / "tracked.txt").write_text("tested tree\n", encoding="utf-8")
        self.git("init", "-q")
        self.git("add", ".")
        self.git(
            "-c",
            "user.name=DWCO Test",
            "-c",
            "user.email=dwco@example.invalid",
            "commit",
            "-qm",
            "test fixture",
        )
        self.head = self.git("rev-parse", "HEAD").stdout.strip()
        self.pass_file = Path(
            self.git(
                "rev-parse", "--git-path", "dwco-pre-push.last-pass"
            ).stdout.strip()
        )
        if not self.pass_file.is_absolute():
            self.pass_file = self.root / self.pass_file
        self.lock_dir = Path(
            self.git("rev-parse", "--git-path", "dwco-pre-push.lock").stdout.strip()
        )
        if not self.lock_dir.is_absolute():
            self.lock_dir = self.root / self.lock_dir
        self.write_valid_receipt()
        self.pass_file.write_text(f"{self.head}\n", encoding="utf-8")
        self.write_attestation_stub("exit 99")

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        )

    def digest(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def write_valid_receipt(self) -> None:
        receipt = {
            "result": "PASS",
            "sourceCommit": self.head,
            "finalCommit": self.head,
            "worktreeClean": True,
            "gateExitCode": 0,
            "workflowSha256": self.digest(self.root / ".github/workflows/ci.yml"),
            "gateScriptSha256": self.digest(self.root / "scripts/ci-local.sh"),
        }
        (self.root / ".local-ci/latest.json").write_text(
            json.dumps(receipt), encoding="utf-8"
        )

    def write_attestation_stub(self, body: str) -> None:
        path = self.root / "scripts/ci-local-attest.sh"
        path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
        path.chmod(0o755)

    def run_hook(self, lines: str) -> subprocess.CompletedProcess[str]:
        environment = dict(os.environ)
        environment["PYTHON_BIN"] = sys.executable
        return subprocess.run(
            [str(self.root / ".githooks/pre-push"), "origin", "unused"],
            cwd=self.root,
            env=environment,
            input=lines,
            capture_output=True,
            text=True,
            check=False,
        )

    def push_line(self, sha: str) -> str:
        return f"refs/heads/test {sha} refs/heads/test {ZERO_SHA}\n"

    def test_matching_pushed_sha_reuses_exact_receipt(self) -> None:
        result = self.run_hook(self.push_line(self.head))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Reusing the successful DWCO verification", result.stdout)

    def test_different_pushed_sha_is_rejected_before_attestation(self) -> None:
        marker = self.root / "attestation-ran"
        self.write_attestation_stub(f"touch '{marker}'\nexit 0")

        result = self.run_hook(self.push_line("f" * 40))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing to push", result.stdout)
        self.assertFalse(marker.exists())

    def test_successful_command_with_invalid_receipt_is_rejected(self) -> None:
        self.pass_file.unlink()
        (self.root / ".local-ci/latest.json").unlink()
        self.write_attestation_stub("printf '{}\\n' > .local-ci/latest.json\nexit 0")

        result = self.run_hook(self.push_line(self.head))

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("did not produce a valid receipt", result.stdout)
        self.assertFalse(self.pass_file.exists())

    def test_stale_lock_is_recovered(self) -> None:
        self.lock_dir.mkdir()
        (self.lock_dir / "pid").write_text("99999999\n", encoding="utf-8")

        result = self.run_hook(self.push_line(self.head))

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Recovered a stale", result.stdout)
        self.assertFalse(self.lock_dir.exists())


class AttestationScriptTests(unittest.TestCase):
    def test_receipt_serialization_failure_is_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".github/workflows").mkdir(parents=True)
            (root / "scripts").mkdir()
            shutil.copy2(
                REPOSITORY_ROOT / "scripts/ci-local-attest.sh",
                root / "scripts/ci-local-attest.sh",
            )
            (root / ".github/workflows/ci.yml").write_text(
                "name: test\n", encoding="utf-8"
            )
            (root / "scripts/ci-local.sh").write_text(
                "#!/bin/sh\nexit 0\n", encoding="utf-8"
            )
            (root / "scripts/ci-local.sh").chmod(0o755)
            python_wrapper = root / "controlled-python"
            python_wrapper.write_text(
                "#!/bin/sh\n"
                'case "$1" in\n'
                "  --version) echo 'Python 3.12.0'; exit 0 ;;\n"
                f"  -c) exec '{sys.executable}' \"$@\" ;;\n"
                "  -) exit 42 ;;\n"
                "esac\n"
                "exit 42\n",
                encoding="utf-8",
            )
            python_wrapper.chmod(0o755)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(
                [
                    "git",
                    "-c",
                    "user.name=DWCO Test",
                    "-c",
                    "user.email=dwco@example.invalid",
                    "commit",
                    "-qm",
                    "test fixture",
                ],
                cwd=root,
                check=True,
            )
            environment = dict(os.environ)
            environment["PYTHON_BIN"] = str(python_wrapper)

            result = subprocess.run(
                [str(root / "scripts/ci-local-attest.sh")],
                cwd=root,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / ".local-ci/latest.json").exists())
            self.assertIn("failed before a valid receipt", result.stderr)


if __name__ == "__main__":
    unittest.main()
