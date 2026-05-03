PYTHON ?= python3
VENV := .venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
UVICORN := $(VENV)/bin/uvicorn
NPM := npm --prefix apps/web

.PHONY: setup ensure api web dev test

setup:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -e ".[dev]"
	$(NPM) install

ensure:
	@test -x "$(UVICORN)" || (echo "Python dependencies missing; running make setup..." && $(MAKE) setup)
	@test -d "apps/web/node_modules" || (echo "Web dependencies missing; installing..." && $(NPM) install)

api: ensure
	$(UVICORN) apps.api.app.main:app --reload

web: ensure
	cd apps/web && npm run dev

dev: ensure
	@echo "Starting API at http://localhost:8000 and Web at http://localhost:3000"
	@trap 'kill $$API_PID $$WEB_PID 2>/dev/null || true' INT TERM EXIT; \
	$(UVICORN) apps.api.app.main:app --reload & API_PID=$$!; \
	(cd apps/web && npm run dev) & WEB_PID=$$!; \
	wait

test:
	$(PYTEST)
	cd apps/web && npm run build
