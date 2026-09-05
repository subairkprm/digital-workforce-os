.PHONY: backend-check backend-test ci-local-fast ci-local compose-up compose-down
backend-check:
	cd backend && ruff check . && ruff format --check . && mypy app
backend-test:
	cd backend && pytest --cov=app
ci-local-fast:
	./scripts/ci-local-fast.sh
ci-local:
	./scripts/ci-local.sh
compose-up:
	docker compose up --build
compose-down:
	docker compose down -v
