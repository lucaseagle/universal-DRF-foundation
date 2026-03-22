# DRF API Template

A clean starter template for building Django REST Framework APIs.

## What this template includes

- Django + Django REST Framework
- OpenAPI generation via `drf-spectacular`
- Health endpoint (`/api/health/`)
- Ruff, Black, Mypy, Pytest
- Pre-commit hooks + Conventional Commits checks
- Dockerfile (builder/development/runtime stages)
- Docker Compose for local API development
- GitHub Actions CI with schema drift checks and Schemathesis

## Requirements

- Python 3.12.x
- `uv`
- `make`
- Optional: Docker + Docker Compose v2

## Installation

```bash
git clone <your-repo-url>
cd <your-repo-name>
make install
pre-commit install
```

## Environment

Create a local env file from the template:

```bash
cp .env.example .env
```

Default configuration is SQLite-based and works out of the box.

## Run locally (without Docker)

```bash
make run
```

The command runs migrations and starts Django at `http://127.0.0.1:8000`.

## Run with Docker

```bash
make dev-up
```

Stop containers:

```bash
make dev-down
```

Remove containers and volumes:

```bash
make hard-dev-down
```

## Quality commands

- `make fmt`
- `make lint`
- `make typecheck`
- `make test`
- `make ci`

## API docs

- OpenAPI schema: `/api/schema/`
- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`

## Extending the template

1. Add your domain apps in `src/`.
2. Register app modules in `src/config/settings.py`.
3. Add URLs in `src/config/urls.py`.
4. Update and commit `openapi/schema.yaml` after API changes.

## Commit convention

This repository uses Conventional Commits.

Examples:

- `feat(api): add invoices endpoint`
- `fix(auth): handle expired token`
- `docs: update local setup instructions`
