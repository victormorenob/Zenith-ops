# Stage 1: Build and install dependencies
FROM python:3.12-slim AS builder

RUN pip install uv==0.11.11

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Stage 2: Runtime — Alembic migrations only (no seed scripts)
FROM python:3.12-slim AS runtime

RUN addgroup --system --gid 1000 app \
    && adduser --system --uid 1000 app

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
COPY alembic.ini ./
COPY src/db/migrations/ ./src/db/migrations/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src:$PYTHONPATH"

USER app

CMD ["alembic", "upgrade", "head"]
