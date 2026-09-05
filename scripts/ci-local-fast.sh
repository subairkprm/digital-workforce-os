#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
ci_venv="$repo_dir/backend/.ci-venv"
dwco_runtime_deps=${CODEX_RUNTIME_DEPS:-}
dwco_user_bin=${XDG_BIN_HOME:-}
if [ -n "${HOME:-}" ]; then
  [ -n "$dwco_runtime_deps" ] || dwco_runtime_deps="${XDG_CACHE_HOME:-$HOME/.cache}/codex-runtimes/codex-primary-runtime/dependencies"
  [ -n "$dwco_user_bin" ] || dwco_user_bin="$HOME/.local/bin"
fi

if [ -n "${NODE_BIN:-}" ]; then node_cmd=$NODE_BIN
elif command -v node >/dev/null 2>&1; then node_cmd=$(command -v node)
elif [ -n "$dwco_user_bin" ] && [ -x "$dwco_user_bin/node" ]; then node_cmd="$dwco_user_bin/node"
else echo "Node.js is required"; exit 1
fi
PATH=$(dirname "$node_cmd"):$PATH
export PATH

if [ -n "${PNPM_BIN:-}" ]; then
  pnpm_cmd=$PNPM_BIN
elif command -v pnpm >/dev/null 2>&1; then
  pnpm_cmd=pnpm
elif [ -n "$dwco_runtime_deps" ] && [ -x "$dwco_runtime_deps/bin/fallback/pnpm" ]; then
  pnpm_cmd="$dwco_runtime_deps/bin/fallback/pnpm"
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

echo "[1/5] Backend lint, types and tests"
cd "$repo_dir/backend"
"$ci_venv/bin/python" -m ruff check .
"$ci_venv/bin/python" -m ruff format --check .
"$ci_venv/bin/python" -m mypy app
"$ci_venv/bin/python" -m pytest -q

echo "[2/5] Admin types and tests"
cd "$repo_dir/admin-web"
"$pnpm_cmd" run typecheck
"$pnpm_cmd" run test

echo "[3/5] Mobile types and dependency compatibility"
cd "$repo_dir/mobile"
"$pnpm_cmd" run typecheck
"$pnpm_cmd" run test
"$pnpm_cmd" run doctor

echo "[4/5] Governance evidence and browser syntax"
cd "$repo_dir/governance-data"
"$ci_venv/bin/python" -m unittest discover -v
"$node_cmd" --check "$repo_dir/governance-web/app.js"

echo "[5/5] Repository safety and workflow validation"
cd "$repo_dir"
test -f AGENTS.md
test -f ARCHITECTURE.md
test -f SECURITY.md
test -f IMPLEMENTATION_PLAN.md
test -f docker-compose.yml
"$ci_venv/bin/python" -c 'import pathlib,yaml; yaml.safe_load(pathlib.Path(".github/workflows/ci.yml").read_text())'
git diff --check
if git ls-files | grep -E '(^|/)\.env($|\.)' | grep -v '\.env\.example$'; then
  echo "Tracked dotenv secret file detected"
  exit 1
fi

echo "LOCAL_CI_FAST=PASS"
