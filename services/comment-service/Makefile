install:
	poetry install

run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8300

migrate:
	poetry run alembic upgrade head

gen-migration:
	poetry run alembic revision --autogenerate -m "migration"

test:
	poetry run pytest -q