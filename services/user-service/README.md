# User Service

The **User Service** is a microservice responsible for managing user accounts in the platform.  
It provides RESTful APIs, gRPC endpoints, and integrates with Kafka for event-driven communication.  

---

## 🚀 Features
- User registration & profile management
- JWT-based authentication (via `auth-service`)
- PostgreSQL for relational persistence
- Redis for caching sessions
- Kafka for event streaming
- gRPC for inter-service communication
- Docker & Poetry-based builds
- CI/CD with GitHub Actions

---

## 🛠️ Tech Stack
- **Python** 3.11+
- **FastAPI** (REST API)
- **gRPC** (service-to-service)
- **SQLAlchemy** + **Alembic** (Postgres migrations)
- **Kafka** (async messaging)
- **Redis** (caching, session store)
- **Docker Compose** (local setup)

---

## 📦 Setup

### 1️⃣ Clone & Install
```bash
git clone https://github.com/Abdumalik-ProDev/ProStream.git
cd user-service
poetry install