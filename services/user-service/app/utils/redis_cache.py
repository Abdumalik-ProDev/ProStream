import aioredis
from app.core.config import settings


_redis = None

def get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
        return _redis