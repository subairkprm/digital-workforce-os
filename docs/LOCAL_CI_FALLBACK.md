# Local CI fallback

GitHub Actions is the required remote CI authority, but the repository owner's billing lock currently
prevents workflows from starting. This fallback does not create a remote status check and does not
replace branch protection. It provides an enforceable local gate until GitHub restores Actions.

## Run the fast gate

```sh
make ci-local-fast
```

The fast gate reuses dependencies prepared by the complete gate. It runs backend lint, formatting,
typing and tests; admin types and tests; mobile types and dependency compatibility; plus workflow
and repository safety validation. The versioned pre-commit hook runs this gate automatically, so
most defects are caught without waiting for Docker builds or dependency installation.

## Run the complete gate

```sh
make ci-local
```

The gate uses an isolated cached Python environment and runs backend lint, formatting, typing,
tests, coverage and dependency audit; Alembic upgrade/downgrade; admin tests and production build;
mobile checks; workflow and secret validation; and Docker startup with PostgreSQL, Redis, migration
and readiness verification. The scripts resolve their required runtimes and Docker credential helper
explicitly so they also work inside GitHub Desktop's restricted process environment.

Docker verification uses the separate `dwco-ci` Compose project and CI-only host ports `18000`,
`15432`, and `16379`. Cleanup removes only that project's disposable containers and volumes. It does
not stop the normal development stack or delete its `dwco_postgres` volume. The project name and
ports can be overridden with `DWCO_CI_COMPOSE_PROJECT`, `DWCO_CI_API_PORT`,
`DWCO_CI_POSTGRES_PORT`, and `DWCO_CI_REDIS_PORT` when another local service already uses them.

## Enable the pre-push gate

This checkout is configured with:

```sh
git config core.hooksPath .githooks
```

Git and GitHub Desktop commits from this checkout invoke the fast gate. Pushes invoke the complete
gate and reject the push if any check fails. Other clones must run the configuration command once.
Bypassing hooks is prohibited by the DWCO engineering process while remote CI is unavailable.

## Limitations

- Results exist only on the trusted local machine and are not independently attested by GitHub.
- GitHub branch protection cannot require this local result.
- DWCO-009 remains open until GitHub Actions runs successfully and required remote checks are enabled.
- This fallback never deploys software or uses production credentials.
