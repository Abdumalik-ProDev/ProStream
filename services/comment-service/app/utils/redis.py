import redis.asyncio as redis
from app.core.config import settings

_redis: redis.Redis | None = None

def get_redis_client() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(settings.REDIS_URL, encoding="utf-8" ,decode_responses=True)
    return _redis

async def cache_comment(video_id: str, comment_id: str, data: dict, expire: int = 60) -> None:
    client = get_redis_client()
    await client.hset(f"comment:{comment_id}", mapping=data)
    await client.expire(f"comment:{comment_id}", expire)
    await client.sadd(f"video_comments:{video_id}", comment_id)

async def get_cached_comment(video_id: str, comment_id: str) -> dict | None:
    client = get_redis_client()
    exists = await client.sismember(f"video_comments:{video_id}", comment_id)
    if not exists:
        return None
    data = await client.hgetall(f"comment:{comment_id}")
    return data if data else None