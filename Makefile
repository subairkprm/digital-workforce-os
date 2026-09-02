.PHONY: backend-check backend-test compose-up compose-down
backend-check:
	cd backend && ruff check . && ruff format --check . && mypy app
backend-test:
	cd backend && pytest --cov=app
compose-up:
	docker compose up --build
compose-down:
	docker compose down -v
