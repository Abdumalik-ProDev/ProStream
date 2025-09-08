import aioredis
from app.core.config import settings

_redis = None

async def get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis

async def blacklist_jti(jti: str, ttl: int):
    r = await get_redis()
    await r.set(f"blk:jti:{jti}", "1", ex=ttl)

async def is_jti_blacklisted(jti: str) -> bool:
    r = await get_redis()
    v = await r.get(f"blk:jti:{jti}")
    return v is not None