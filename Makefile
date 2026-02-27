# Makefile — The Grand Meridian Guest Services
#
# HOW TO USE:
#   make setup   — Full setup: create venv, install deps, seed DB
#   make install — Create .venv and pip install -r requirements.txt
#   make seed    — Populate database (guests, staff, requests)
#   make dev     — Run server at http://localhost:8000
#   make test    — Run pytest
#   make test-report — Pytest + HTML report (open report.html)
#
# DEBUGGING:
#   - "command not found": ensure you're in project root
#   - "venv not found": run make install first
#   - Tests fail: DATABASE_URL set to test_guest_services_full.db in conftest
#
.PHONY: setup install seed dev test

setup: install seed  ## Full setup: install deps + seed DB

install:  ## Create venv and install dependencies
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

seed:  ## Populate database with sample data
	.venv/bin/python -m app.seed

dev:  ## Run dev server with hot reload
	.venv/bin/python -m uvicorn app.main:app --reload --port 8000

test:  ## Run pytest
	.venv/bin/python -m pytest tests/ -v

test-report:  ## Run pytest and generate HTML report (open report.html in browser)
	.venv/bin/python -m pytest tests/ -v --html=report.html --self-contained-html
