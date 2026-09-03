#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if [ -n "${NODE_BIN:-}" ]; then node_cmd=$NODE_BIN
elif command -v node >/dev/null 2>&1; then node_cmd=$(command -v node)
elif [ -x /Users/subair/.local/bin/node ]; then node_cmd=/Users/subair/.local/bin/node
else echo "Node.js is required"; exit 1
fi
PATH=$(dirname "$node_cmd"):$PATH
if [ -d /Applications/Docker.app/Contents/Resources/bin ]; then
  PATH=/Applications/Docker.app/Contents/Resources/bin:$PATH
fi
export PATH
if [ -n "${PYTHON_BIN:-}" ]; then python_cmd=$PYTHON_BIN
elif [ -x /Users/subair/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 ]; then python_cmd=/Users/subair/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
else python_cmd=python3
fi
if [ -n "${PNPM_BIN:-}" ]; then pnpm_cmd=$PNPM_BIN
elif command -v pnpm >/dev/null 2>&1; then pnpm_cmd=pnpm
elif [ -x /Users/subair/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm ]; then pnpm_cmd=/Users/subair/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/pnpm
else echo "pnpm is required"; exit 1
fi
if [ -n "${DOCKER_BIN:-}" ]; then docker_cmd=$DOCKER_BIN
elif command -v docker >/dev/null 2>&1; then docker_cmd=docker
elif [ -x /Applications/Docker.app/Contents/Resources/bin/docker ]; then docker_cmd=/Applications/Docker.app/Contents/Resources/bin/docker
else echo "Docker Desktop is required"; exit 1
fi
ci_venv="$repo_dir/backend/.ci-venv"
compose_started=0

cleanup() {
  if [ "$compose_started" -eq 1 ]; then
    "$docker_cmd" compose -f "$repo_dir/docker-compose.yml" --project-directory "$repo_dir" down -v
  fi
}
trap cleanup EXIT INT TERM

echo "[1/7] Preparing isolated Python environment"
if [ ! -x "$ci_venv/bin/python" ]; then
  "$python_cmd" -m venv "$ci_venv"
fi
"$ci_venv/bin/python" -m pip install --upgrade pip >/dev/null
"$ci_venv/bin/python" -m pip install -e "$repo_dir/backend[dev]" >/dev/null

echo "[2/7] Backend lint, types, tests, coverage and dependency audit"
cd "$repo_dir/backend"
"$ci_venv/bin/python" -m ruff check .
"$ci_venv/bin/python" -m ruff format --check .
"$ci_venv/bin/python" -m mypy app
"$ci_venv/bin/python" -m pytest --cov=app --cov-report=term-missing
"$ci_venv/bin/python" -m pip_audit --skip-editable

echo "[3/7] Alembic upgrade and downgrade"
ci_tmp_dir=$(mktemp -d)
ci_db_path="$ci_tmp_dir/dwco.db"
DWCO_DATABASE_URL="sqlite:///$ci_db_path" "$ci_venv/bin/python" -m alembic upgrade head
DWCO_DATABASE_URL="sqlite:///$ci_db_path" "$ci_venv/bin/python" -m alembic downgrade base
DWCO_DATABASE_URL="sqlite:///$ci_db_path" "$ci_venv/bin/python" -m alembic upgrade head
unlink "$ci_db_path"
rmdir "$ci_tmp_dir"

echo "[4/7] Admin install, types, tests, build and audit"
cd "$repo_dir/admin-web"
"$pnpm_cmd" install --frozen-lockfile
"$pnpm_cmd" run typecheck
"$pnpm_cmd" run test
"$pnpm_cmd" run build
"$pnpm_cmd" audit --audit-level high

echo "[5/7] Mobile install, types, dependency check and audit"
cd "$repo_dir/mobile"
"$pnpm_cmd" install --frozen-lockfile
"$pnpm_cmd" run typecheck
"$pnpm_cmd" run doctor
"$pnpm_cmd" audit --audit-level high

echo "[6/7] Repository and workflow validation"
cd "$repo_dir"
"$ci_venv/bin/python" -c 'import pathlib,yaml; yaml.safe_load(pathlib.Path(".github/workflows/ci.yml").read_text())'
git diff --check
if git ls-files | grep -E '(^|/)\.env($|\.)' | grep -v '\.env\.example$'; then
  echo "Tracked dotenv secret file detected"
  exit 1
fi

echo "[7/7] Docker build, migration and live readiness"
"$docker_cmd" compose config --quiet
"$docker_cmd" compose up -d --build
compose_started=1
attempt=0
until curl --silent --show-error --fail http://localhost:8000/readyz >/dev/null; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge 30 ]; then
    "$docker_cmd" compose logs --no-color api
    exit 1
  fi
  sleep 2
done
curl --silent --show-error --fail http://localhost:8000/health >/dev/null
curl --silent --show-error --fail http://localhost:8000/livez >/dev/null
test "$("$docker_cmd" compose exec -T postgres psql -U dwco -d dwco -tAc 'select version_num from alembic_version;')" = "0002_admin_security"
test "$("$docker_cmd" compose exec -T redis redis-cli ping)" = "PONG"

echo "LOCAL_CI=PASS"
