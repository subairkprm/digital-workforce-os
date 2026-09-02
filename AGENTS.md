# AGENTS.md — DWCO Engineering Rules

## Authority
This repository is the canonical source authority for Digital Workforce Communication OS code.

## Agent execution rules
1. Inspect existing source before editing.
2. Work only within the assigned implementation contract.
3. Do not restructure unrelated modules.
4. Every database schema change requires a migration.
5. Every endpoint requires authentication, tenant-scope, authorization and validation analysis.
6. Every external provider must sit behind an adapter.
7. Never commit credentials, tokens, certificates or production secrets.
8. Never expose provider-specific payloads directly to client applications.
9. Every administrative mutation must emit an audit event.
10. Add/update automated tests for every behavior changed.
11. Run lint, type checks, tests and build before reporting completion.
12. Report known gaps and deferred scope explicitly.
13. Do not deploy or mutate production unless a separate, explicit deployment contract authorizes it.
14. Do not add PSTN, eSIM, AI, recording or Teams functionality to DWCO 0.1 unless separately authorized.

## Completion report
Every contract must report:
- contract ID
- files changed
- database changes
- API changes
- security changes
- tests
- build result
- known issues
- deferred scope
- deployment status
- rollback guidance
