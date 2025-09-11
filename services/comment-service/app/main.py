import asyncio, logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.db import Base, engine
from app.api import comments
from app.utils.redis import init_redis, close_redis
from app.utils.kafka import init_kafka, close_kafka

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Lifespan Context (startup & shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting up %s", settings.project_name)

    # Init DB
    logger.info("Initializing database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Init Redis
    logger.info("Connecting to Redis...")
    await init_redis()

    # Init Kafka
    logger.info("Connecting to Kafka...")
    await init_kafka()

    yield

    # Shutdown logic
    logger.info("Shutting down services...")

    await close_kafka()
    await close_redis()

    logger.info("🛑 Shutdown complete")


# --- FastAPI App ---
app = FastAPI(
    title=settings.project_name,
    lifespan=lifespan
)

# Routers
app.include_router(comments.router, prefix="/comments", tags=["comments"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.project_name}