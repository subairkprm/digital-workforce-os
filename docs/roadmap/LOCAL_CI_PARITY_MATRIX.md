# Local CI parity matrix

STATUS=ACTIVE_MITIGATION_NOT_REMOTE_ATTESTATION

| GitHub Actions job | Required remote checks | Local equivalent | Residual difference |
|---|---|---|---|
| Repository baseline | Dotenv rejection and required repository files | Steps 6 plus both local gates | Local machine is not a protected GitHub check |
| Backend | Python 3.12 install, lint, format, mypy, pytest/coverage, pip audit | Complete steps 1–3 | macOS runner rather than GitHub Ubuntu |
| Admin web | pnpm install, typecheck, tests, build, audit on Node 22 | Complete step 4 | Receipt records installed Node; exact major may differ |
| Mobile | pnpm install, typecheck, tests, Expo doctor, audit on Node 22 | Complete step 5 | No physical iOS/Android device validation |
| Governance control plane | Unit/static tests, JavaScript syntax, Compose config | Complete step 6 and Docker step 7 | No hosted browser or accessibility audit |
| Docker | Build, startup, readiness, cleanup | Complete step 7 in isolated `dwco-ci` project | Local Docker Desktop/arm64 rather than hosted Linux |
| Additional local evidence | Migration round-trip, PostgreSQL migration version, Redis ping, live governance survival | Complete steps 3 and 7 | Additional evidence; not a remote status check |

## Pass rule

A local receipt is `PASS` only when the worktree is clean before and after the complete gate, the
source and final commit are identical, every command passes, the isolated Compose project is removed,
and the fixed no-deployment boundary is retained. Any failure, interrupt, dirty tree, or changed
commit produces `FAIL`.

## Exit rule

Retire this mitigation only after GitHub Actions has a successful run for the same repository state,
required checks are configured on protected `main`, and DevOps/SRE records the evidence.
