# syntax=docker/dockerfile:1

FROM python:3.13.14-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_VERSION=0.11.32 \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

RUN pip install --no-cache-dir "uv==${UV_VERSION}"

COPY pyproject.toml uv.lock README.md .python-version ./


RUN uv sync \
    --locked \
    --no-dev \
    --no-install-project

COPY app ./app
COPY migrations ./migrations
COPY scripts ./scripts
COPY data ./data
COPY alembic.ini ./

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]