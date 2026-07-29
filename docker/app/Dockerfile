# syntax=docker/dockerfile:1

ARG PYTHON_IMAGE=python:3.13.14-slim-bookworm@sha256:9d7f287598e1a5a978c015ee176d8216435aaf335ed69ac3c38dd1bbb10e8d64

FROM ${PYTHON_IMAGE} AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_VERSION=0.11.32 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy

WORKDIR /build

RUN pip install \
    --no-cache-dir \
    "uv==${UV_VERSION}"

COPY pyproject.toml uv.lock README.md .python-version ./

RUN uv sync \
    --locked \
    --no-dev \
    --no-install-project


FROM ${PYTHON_IMAGE} AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

RUN groupadd \
        --gid 10001 \
        appgroup \
    && useradd \
        --uid 10001 \
        --gid appgroup \
        --create-home \
        --shell /usr/sbin/nologin \
        appuser

COPY --from=builder \
    --chown=appuser:appgroup \
    /opt/venv \
    /opt/venv

COPY --chown=appuser:appgroup app ./app
COPY --chown=appuser:appgroup migrations ./migrations
COPY --chown=appuser:appgroup scripts ./scripts
COPY --chown=appuser:appgroup data ./data
COPY --chown=appuser:appgroup alembic.ini ./

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
