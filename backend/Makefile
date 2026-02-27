.PHONY: help seed migrate run test

VENV_PYTHON := .venv/bin/python

help:
	@echo "Targets:"
	@echo "  make seed     # Seed initial development data"
	@echo "  make migrate  # Run alembic migrations"
	@echo "  make run      # Start API with reload"
	@echo "  make test     # Run backend tests"

seed:
	@$(VENV_PYTHON) scripts/seed.py

migrate:
	@$(VENV_PYTHON) -m alembic upgrade head

run:
	@$(VENV_PYTHON) -m uvicorn app.main:app --reload

test:
	@$(VENV_PYTHON) -m pytest -q
