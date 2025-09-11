# Comment Service

Provides comment creation, listing and deletion for ProStream.

## Quickstart (dev)

1. Copy `.env.example` → `.env` and set values (use same AUTH_SERVICE_JWT_SECRET as auth-service).
2. Start infra:
   ```bash
   docker compose up -d db redis zookeeper kafka