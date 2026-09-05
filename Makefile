.PHONY: backend-check backend-test ci-local-fast ci-local ci-local-attest compose-up compose-down
backend-check:
	cd backend && ruff check . && ruff format --check . && mypy app
backend-test:
	cd backend && pytest --cov=app
ci-local-fast:
	./scripts/ci-local-fast.sh
ci-local:
	./scripts/ci-local.sh
ci-local-attest:
	./scripts/ci-local-attest.sh
compose-up:
	docker compose up --build
compose-down:
	docker compose down -v
