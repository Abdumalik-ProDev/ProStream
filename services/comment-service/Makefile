.PHONY: run dev clean format lint test migrate upgrade

# Run the service normally
run:
	@echo "🚀 Starting comment-service..."
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run the service in dev mode (with reload)
dev:
	@echo "🔄 Running comment-service in dev mode..."
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Clean __pycache__ and Python junk
clean:
	@echo "🧹 Cleaning __pycache__ and Python artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	@echo "✨ Clean complete!"

# Format code with black + isort
format:
	@echo "🎨 Formatting code..."
	poetry run black app
	poetry run isort app

# Lint with mypy + flake8
lint:
	@echo "🔍 Linting code..."
	poetry run mypy app
	poetry run flake8 app

# Run tests
test:
	@echo "🧪 Running tests..."
	poetry run pytest -v

# Alembic migrations
migrate:
	@echo "📦 Creating new migration..."
	poetry run alembic revision --autogenerate -m "auto migration"

upgrade:
	@echo "⬆️ Applying migrations..."
	poetry run alembic upgrade head