# Local CI fallback

GitHub Actions remains the required remote CI authority, but the repository owner's recorded
account/workflow-startup limitation currently prevents usable runs. The local fallback rejects
commits and pushes that fail the corresponding checks and can produce a sanitized, exact-commit
receipt. It does not create a GitHub status check, replace branch protection, or authorize a release.

## Fast developer gate

```sh
make ci-local-fast
```

The fast gate reuses dependencies prepared by the complete gate. It runs backend lint, formatting,
typing and tests; admin types and tests; mobile types, tests, and dependency compatibility;
governance tests and browser syntax; repository structure, workflow YAML, diff, and secret checks.
The versioned pre-commit hook runs this gate automatically.

## Complete parity gate

```sh
make ci-local
```

The complete gate additionally runs backend coverage and dependency audit; Alembic
upgrade/downgrade/re-upgrade; admin production build and audit; mobile audit; Compose validation;
and an isolated Docker startup with PostgreSQL, Redis, migrations, and readiness checks. See
[`docs/roadmap/LOCAL_CI_PARITY_MATRIX.md`](roadmap/LOCAL_CI_PARITY_MATRIX.md) for the mapping to
GitHub Actions.

Docker verification uses the separate `dwco-ci` Compose project and CI-only host ports `13100`,
`18000`, `15432`, and `16379`. Cleanup removes only that project's disposable containers and
volumes. It does not stop the normal development stack or delete its `dwco_postgres` volume. The
project name and ports can be overridden with `DWCO_CI_COMPOSE_PROJECT`,
`DWCO_CI_GOVERNANCE_PORT`, `DWCO_CI_API_PORT`, `DWCO_CI_POSTGRES_PORT`, and
`DWCO_CI_REDIS_PORT`.

## Exact-commit receipt

Run the complete gate against a clean worktree and write a receipt:

```sh
make ci-local-attest
```

The receipt writer refuses a dirty source tree, detects a changed `HEAD`, records failures and
interruptions, and writes atomically to `.local-ci/latest.json` plus a commit-named local copy. Both
JSON files are ignored by Git. The receipt contains only result, commit, branch, timestamps,
duration, gate/workflow hashes, clean-tree state, runner versions, and fixed security boundaries. It
does not capture environment variables, filesystem paths, usernames, network addresses, credentials,
or customer data.

The local governance service mounts `.local-ci` read-only and displays a validated, normalized copy.
Missing receipts show `NOT RUN`; malformed or out-of-boundary receipts show `INVALID` without
making the wider governance snapshot unavailable.

## Enable the local hooks

This checkout is configured with:

```sh
git config core.hooksPath .githooks
```

Git and GitHub Desktop commits invoke the fast gate. Pushes invoke the exact-commit complete gate and
reject the push if it fails. A cached result is reused only when both the cache and a valid passing
receipt match the current `HEAD`. Other clones must run the configuration command once. Bypassing
hooks is prohibited by the DWCO engineering process while remote CI is unavailable.

## Trust and release limits

- The receipt is evidence from one trusted local machine, not independent attestation.
- The current local runner may differ from GitHub's Ubuntu/Node 22 runner; the exact versions are
  visible in the receipt. A pass proves this checkout on the recorded runner, not universal parity.
- GitHub branch protection cannot require the local result.
- DWCO-009 and DEP-001 remain open until GitHub Actions passes and required checks are protected.
- This fallback never deploys software, accesses production, grants legal approval, or makes the
  product ready by itself.
