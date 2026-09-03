# Local CI fallback

GitHub Actions is the required remote CI authority, but the repository owner's billing lock currently
prevents workflows from starting. This fallback does not create a remote status check and does not
replace branch protection. It provides an enforceable local gate until GitHub restores Actions.

## Run the complete gate

```sh
make ci-local
```

The gate uses an isolated cached Python environment and runs backend lint, formatting, typing,
tests, coverage and dependency audit; Alembic upgrade/downgrade; admin tests and production build;
mobile checks; workflow and secret validation; and Docker startup with PostgreSQL, Redis, migration
and readiness verification.

## Enable the pre-push gate

This checkout is configured with:

```sh
git config core.hooksPath .githooks
```

Git and GitHub Desktop pushes from this checkout invoke the complete gate and reject the push if any
check fails. Other clones must run the configuration command once. Bypassing hooks is prohibited by
the DWCO engineering process while remote CI is unavailable.

## Limitations

- Results exist only on the trusted local machine and are not independently attested by GitHub.
- GitHub branch protection cannot require this local result.
- DWCO-009 remains open until GitHub Actions runs successfully and required remote checks are enabled.
- This fallback never deploys software or uses production credentials.
