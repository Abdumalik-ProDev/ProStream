FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* /app/
RUN pip install --upgrade pip poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY . /app
ENV PYTHONPATH=/app
EXPOSE 8300 50054

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8300"]