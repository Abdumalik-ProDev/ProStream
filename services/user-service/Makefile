
---

# 🏗️ `Makefile`

```makefile
# Variables
SERVICE_NAME = user-service
PORT = 8001

# Install dependencies
install:
	poetry install

# Format code
format:
	poetry run black .
	poetry run isort .
	poetry run flake8 .

# Run service locally
run:
	poetry run uvicorn main:app --reload --host 0.0.0.0 --port $(PORT)

# Run tests
test:
	poetry run pytest -v --disable-warnings --maxfail=1

# Run alembic migrations
migrate:
	poetry run alembic upgrade head

# Generate new migration
revision:
	poetry run alembic revision --autogenerate -m "new migration"

# Docker build & run
docker-build:
	docker build -t $(SERVICE_NAME):latest .

docker-run:
	docker run -p $(PORT):$(PORT) $(SERVICE_NAME):latest

# Clean
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +