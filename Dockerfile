FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

COPY src/ ./src/
COPY migrations/ ./migrations/
COPY alembic.ini .

ENV PYTHONPATH=/app/src
EXPOSE 8000
