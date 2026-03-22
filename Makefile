.PHONY: install fmt lint typecheck test ci schemathesis dev-up dev-down hard-dev-down logs sh-api test-api env-meta

# Force temp files onto a POSIX path (pytest capture breaks on WSL temp dirs)
export TMPDIR ?= /tmp

# for using active venv (VIRTUAL_ENV)
UV_RUN = uv run --active

# docker-compose wrapper
DOCKER_COMPOSE ?= docker compose
DC_FILE ?= docker-compose.yml
DC := $(DOCKER_COMPOSE) -f $(DC_FILE)

install:
	uv lock
	uv sync --extra dev --frozen
	uv pip install -e .

fmt:
	$(UV_RUN) black .
	$(UV_RUN) ruff check . --fix --unsafe-fixes

lint:
	$(UV_RUN) ruff check .

typecheck:
	$(UV_RUN) mypy src

test: export USE_SQLITE_FOR_TESTS ?= true
test:
	$(UV_RUN) pytest

ci:
	$(MAKE) install
	uv run black --check .
	$(MAKE) lint
	$(MAKE) typecheck
	$(MAKE) test

schemathesis:
	uv run --extra dev python .github/scripts/run_schemathesis.py

run:
	$(UV_RUN) python src/manage.py migrate --noinput
	$(UV_RUN) python src/manage.py runserver 0.0.0.0:8000


dev-up:
	$(DC) up -d --build --remove-orphans api

dev-down:
	$(DC) down --remove-orphans

hard-dev-down:
	$(DC) down --volumes --remove-orphans

logs:
	$(DC) logs -f --tail=200 $(SERVICE)

sh-api:
	$(DC) exec api sh

test-api:
	$(DC) run --rm api make test
