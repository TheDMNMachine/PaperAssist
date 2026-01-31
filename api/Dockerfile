FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*
ADD https://astral.sh/uv/install.sh /tmp/uv-install.sh
RUN sh /tmp/uv-install.sh && mv /root/.local/bin/uv /usr/local/bin/uv && rm /tmp/uv-install.sh

# Install dependencies
COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev --no-install-project

# Copy application and Alembic
COPY app/ app/
COPY alembic.ini ./
COPY alembic/ alembic/

EXPOSE 8000

CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
