.PHONY: install run migrate worker docker-build docker-run gen-migrate test

install:
	poetry install

run:
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8200

migrate:
	poetry run alembic upgrade head

worker:
	poetry run celery -A app.workers.celery_app worker --loglevel=info

docker-build:
	docker build -t video-service:latest .

docker-run:
	docker run -p 8200:8200 video-service:latest

gen-migrate:
	poetry run alembic revision --autogenerate -m "auto migration"

test:
	poetry run pytest -q