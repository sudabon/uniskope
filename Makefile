.PHONY: install dev db-migrate up down test lint

install:
	cd backend && pip install -e ".[dev]"
	cd frontend && npm ci

dev:
	@echo "Start DB: make up (or docker compose up -d db)"
	@echo "Backend: cd backend && uvicorn app.main:app --reload"
	@echo "Frontend: cd frontend && npm run dev"

db-migrate:
	cd backend && alembic upgrade head

up:
	docker compose up -d db
	@echo "Waiting for PostgreSQL..."
	@sleep 3
	$(MAKE) db-migrate

down:
	docker compose down

test:
	cd backend && pytest -v

lint:
	cd backend && ruff check app tests && mypy app
	cd frontend && npm run lint
