#!/bin/sh
set -u

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
receipt_dir="$repo_dir/.local-ci"
latest_receipt="$receipt_dir/latest.json"
receipt_written=0
started_at=$(date -u "+%Y-%m-%dT%H:%M:%SZ")
started_epoch=$(date +%s)

if [ -n "${PYTHON_BIN:-}" ]; then python_cmd=$PYTHON_BIN
elif [ -x /Users/subair/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 ]; then python_cmd=/Users/subair/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
else python_cmd=python3
fi
if [ -n "${NODE_BIN:-}" ]; then node_cmd=$NODE_BIN
elif command -v node >/dev/null 2>&1; then node_cmd=$(command -v node)
elif [ -x /Users/subair/.local/bin/node ]; then node_cmd=/Users/subair/.local/bin/node
else node_cmd=
fi
if [ -n "${PNPM_BIN:-}" ]; then pnpm_cmd=$PNPM_BIN
elif command -v pnpm >/dev/null 2>&1; then pnpm_cmd=$(command -v pnpm)
elif [ -x /Users/subair/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm ]; then pnpm_cmd=/Users/subair/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm
else pnpm_cmd=
fi
if [ -n "${DOCKER_BIN:-}" ]; then docker_cmd=$DOCKER_BIN
elif command -v docker >/dev/null 2>&1; then docker_cmd=$(command -v docker)
elif [ -x /Applications/Docker.app/Contents/Resources/bin/docker ]; then docker_cmd=/Applications/Docker.app/Contents/Resources/bin/docker
else docker_cmd=
fi

mkdir -p "$receipt_dir"

source_commit=$(git -C "$repo_dir" rev-parse HEAD)
source_branch=$(git -C "$repo_dir" symbolic-ref --quiet --short HEAD || printf '%s' DETACHED)
workflow_sha=$($python_cmd -c 'import hashlib,pathlib,sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())' "$repo_dir/.github/workflows/ci.yml")
gate_sha=$($python_cmd -c 'import hashlib,pathlib,sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())' "$repo_dir/scripts/ci-local.sh")

write_receipt() {
  receipt_result=$1
  gate_exit_code=$2
  receipt_note=$3
  completed_at=$(date -u "+%Y-%m-%dT%H:%M:%SZ")
  completed_epoch=$(date +%s)
  duration_seconds=$((completed_epoch - started_epoch))
  final_commit=$(git -C "$repo_dir" rev-parse HEAD 2>/dev/null || printf '%s' UNKNOWN)
  if [ -z "$(git -C "$repo_dir" status --porcelain --untracked-files=normal 2>/dev/null)" ]; then
    worktree_clean=true
  else
    worktree_clean=false
  fi
  python_version=$($python_cmd --version 2>&1 | awk '{print $2}')
  if [ -n "$node_cmd" ]; then node_version=$($node_cmd --version 2>/dev/null | sed 's/^v//'); else node_version=unavailable; fi
  if [ -n "$pnpm_cmd" ]; then pnpm_version=$($pnpm_cmd --version 2>/dev/null || printf '%s' unavailable); else pnpm_version=unavailable; fi
  if [ -n "$docker_cmd" ]; then docker_version=$($docker_cmd version --format '{{.Client.Version}}' 2>/dev/null || printf '%s' unavailable); else docker_version=unavailable; fi
  runner_os=$(uname -s)
  runner_arch=$(uname -m)
  temp_receipt=$(mktemp "$receipt_dir/.latest.XXXXXX")
  RECEIPT_RESULT="$receipt_result" \
  GATE_EXIT_CODE="$gate_exit_code" \
  RECEIPT_NOTE="$receipt_note" \
  SOURCE_COMMIT="$source_commit" \
  FINAL_COMMIT="$final_commit" \
  SOURCE_BRANCH="$source_branch" \
  STARTED_AT="$started_at" \
  COMPLETED_AT="$completed_at" \
  DURATION_SECONDS="$duration_seconds" \
  WORKFLOW_SHA="$workflow_sha" \
  GATE_SHA="$gate_sha" \
  WORKTREE_CLEAN="$worktree_clean" \
  RUNNER_OS="$runner_os" \
  RUNNER_ARCH="$runner_arch" \
  PYTHON_VERSION="$python_version" \
  NODE_VERSION="$node_version" \
  PNPM_VERSION="$pnpm_version" \
  DOCKER_VERSION="$docker_version" \
  "$python_cmd" - "$temp_receipt" <<'PY'
import json
import os
import pathlib
import sys

payload = {
    "schemaVersion": 1,
    "result": os.environ["RECEIPT_RESULT"],
    "sourceCommit": os.environ["SOURCE_COMMIT"],
    "finalCommit": os.environ["FINAL_COMMIT"],
    "sourceBranch": os.environ["SOURCE_BRANCH"],
    "startedAt": os.environ["STARTED_AT"],
    "completedAt": os.environ["COMPLETED_AT"],
    "durationSeconds": int(os.environ["DURATION_SECONDS"]),
    "gateExitCode": int(os.environ["GATE_EXIT_CODE"]),
    "workflowSha256": os.environ["WORKFLOW_SHA"],
    "gateScriptSha256": os.environ["GATE_SHA"],
    "worktreeClean": os.environ["WORKTREE_CLEAN"] == "true",
    "scope": "TRUSTED_LOCAL_MACHINE_ONLY",
    "remoteCiStatus": "UNAVAILABLE_NOT_ATTESTED",
    "deploymentStatus": "NOT_AUTHORIZED_NOT_DEPLOYED",
    "note": os.environ["RECEIPT_NOTE"],
    "runner": {
        "os": os.environ["RUNNER_OS"],
        "arch": os.environ["RUNNER_ARCH"],
        "python": os.environ["PYTHON_VERSION"],
        "node": os.environ["NODE_VERSION"],
        "pnpm": os.environ["PNPM_VERSION"],
        "docker": os.environ["DOCKER_VERSION"],
    },
}
path = pathlib.Path(sys.argv[1])
path.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
PY
  chmod 0644 "$temp_receipt"
  mv "$temp_receipt" "$latest_receipt"
  cp "$latest_receipt" "$receipt_dir/$source_commit.json"
  chmod 0644 "$receipt_dir/$source_commit.json"
  receipt_sha=$($python_cmd -c 'import hashlib,pathlib,sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())' "$latest_receipt")
  receipt_written=1
  printf 'LOCAL_CI_RECEIPT=%s\n' "$latest_receipt"
  printf 'LOCAL_CI_RECEIPT_SHA256=%s\n' "$receipt_sha"
  printf 'LOCAL_CI_RECEIPT_RESULT=%s\n' "$receipt_result"
}

finalize() {
  exit_code=$?
  if [ "$receipt_written" -eq 0 ]; then
    write_receipt FAIL "$exit_code" "Local gate interrupted or aborted before a complete result."
  fi
}
trap finalize EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

if [ -n "$(git -C "$repo_dir" status --porcelain --untracked-files=normal)" ]; then
  write_receipt FAIL 2 "Gate refused: the source tree was not clean."
  exit 2
fi

"$repo_dir/scripts/ci-local.sh"
gate_exit_code=$?
final_commit=$(git -C "$repo_dir" rev-parse HEAD)
if [ "$gate_exit_code" -ne 0 ]; then
  write_receipt FAIL "$gate_exit_code" "The complete local CI gate failed."
  exit "$gate_exit_code"
fi
if [ "$final_commit" != "$source_commit" ]; then
  write_receipt FAIL 3 "Gate refused: HEAD changed while checks were running."
  exit 3
fi
if [ -n "$(git -C "$repo_dir" status --porcelain --untracked-files=normal)" ]; then
  write_receipt FAIL 4 "Gate refused: checks changed the source tree."
  exit 4
fi

write_receipt PASS 0 "Complete local parity gate passed; this is not GitHub-hosted attestation."
exit 0
