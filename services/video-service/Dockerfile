FROM python:3.13-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential ffmpeg libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* /app/
RUN pip install --upgrade pip poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . /app

FROM python:3.13-slim
WORKDIR /app
RUN apt-get update && apt-get install -y ffmpeg libsndfile1 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /app /app
ENV PYTHONPATH=/app
EXPOSE 8200 50053
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8200"]