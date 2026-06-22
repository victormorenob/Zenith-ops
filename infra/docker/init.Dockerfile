FROM python:3.12-slim AS runtime

RUN pip install uv==0.11.11 

WORKDIR /app

COPY README.md pyproject.toml uv.lock ./
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY models/ ./models/
COPY alembic.ini ./

RUN uv sync 

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src:$PYTHONPATH"

CMD python scripts/generate_dummy_model.py && alembic upgrade head