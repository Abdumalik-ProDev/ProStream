# Auth Service (ProStream)

## Quick dev startup
1. Copy `.env` and set secrets.
2. Install deps: `poetry install`
3. Start infra: `docker compose up -d db redis zookeeper kafka`
4. Generate alembic migration (first time):
   `poetry run alembic revision --autogenerate -m "initial"`
5. Run service:
   `docker compose up --build auth`
6. API docs: http://localhost:8000/docs
