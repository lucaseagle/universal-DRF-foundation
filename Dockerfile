############################
# ---- builder ----
############################
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

# (optional) certs – python:3.12-slim should have them, but just in case
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv "$VIRTUAL_ENV" && \
    uv sync --active --frozen --no-dev --no-install-project

COPY src/ ./src/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --no-deps .

############################
# ---- development ----
############################
FROM builder AS development

RUN apt-get update && apt-get install -y --no-install-recommends make curl \
    && rm -rf /var/lib/apt/lists/*

# not necessary, it is just for convenience in dev
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -e ".[dev]"

WORKDIR /app

EXPOSE 8000
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]

############################
# ---- runtime ----
############################
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    APP_HOME="/app"

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /usr/sbin/nologin appuser
WORKDIR ${APP_HOME}

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/src /app/src

USER appuser

EXPOSE 8000
CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]
