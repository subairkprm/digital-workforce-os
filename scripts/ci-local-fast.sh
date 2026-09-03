#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
ci_venv="$repo_dir/backend/.ci-venv"

if [ -n "${PNPM_BIN:-}" ]; then
  pnpm_cmd=$PNPM_BIN
elif command -v pnpm >/dev/null 2>&1; then
  pnpm_cmd=pnpm
elif [ -x /Users/subair/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm ]; then
  pnpm_cmd=/Users/subair/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm
else
  echo "pnpm is required; run make ci-local once to prepare this checkout"
  exit 1
fi

if [ ! -x "$ci_venv/bin/python" ]; then
  echo "Local CI environment is missing; run make ci-local once to prepare this checkout"
  exit 1
fi
if [ ! -d "$repo_dir/admin-web/node_modules" ] || [ ! -d "$repo_dir/mobile/node_modules" ]; then
  echo "Node dependencies are missing; run make ci-local once to prepare this checkout"
  exit 1
fi

echo "[1/4] Backend lint, types and tests"
cd "$repo_dir/backend"
"$ci_venv/bin/python" -m ruff check .
"$ci_venv/bin/python" -m ruff format --check .
"$ci_venv/bin/python" -m mypy app
"$ci_venv/bin/python" -m pytest -q

echo "[2/4] Admin types and tests"
cd "$repo_dir/admin-web"
"$pnpm_cmd" run typecheck
"$pnpm_cmd" run test

echo "[3/4] Mobile types and dependency compatibility"
cd "$repo_dir/mobile"
"$pnpm_cmd" run typecheck
"$pnpm_cmd" run doctor

echo "[4/4] Repository safety and workflow validation"
cd "$repo_dir"
"$ci_venv/bin/python" -c 'import pathlib,yaml; yaml.safe_load(pathlib.Path(".github/workflows/ci.yml").read_text())'
git diff --check
if git ls-files | grep -E '(^|/)\.env($|\.)' | grep -v '\.env\.example$'; then
  echo "Tracked dotenv secret file detected"
  exit 1
fi

echo "LOCAL_CI_FAST=PASS"
