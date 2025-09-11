import logging
import aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)

redis = None


async def init_redis():
    """Initialize Redis connection pool."""
    global redis
    if redis is None:
        try:
            redis = aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("✅ Connected to Redis at %s", settings.redis_url)
        except Exception as e:
            logger.error("❌ Failed to connect Redis: %s", e)
            raise


async def close_redis():
    """Close Redis connection."""
    global redis
    if redis:
        await redis.close()
        logger.info("🛑 Redis connection closed")
        redis = None