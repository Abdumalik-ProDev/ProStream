from typing import AsyncGenerator
from app.core.db import async_session
from app.utils.redis_client import RedisClient
from app.utils.kafka_producer import KafkaProducer
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import UserRepository
from app.repositories.refresh_repo import RefreshTokenRepository

def get_user_repo():
    return UserRepository()

def get_refresh_repo():
    return RefreshTokenRepository()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as s:
        yield s

_redis = None
_kafka = None

async def get_redis():
    global _redis
    if _redis is None:
        _redis = RedisClient()
        await _redis.connect()
    return _redis

async def get_kafka():
    global _kafka
    if _kafka is None:
        _kafka = KafkaProducer()
        await _kafka.start()
    return _kafka