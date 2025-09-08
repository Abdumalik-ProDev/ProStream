# Stage 1: Build
FROM python:3.13-slim AS builder
WORKDIR /app

# System deps for grpc, asyncpg, kafka
RUN apt-get update && apt-get install -y build-essential gcc git

COPY pyproject.toml poetry.lock* /app/
RUN pip install --upgrade pip poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

COPY . /app

# Stage 2: Run
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /app /app

EXPOSE 8000 50051
CMD ["python", "-m", "app.grpc_server"]