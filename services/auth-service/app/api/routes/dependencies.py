from app.core.db import AsyncSessionLocal
from app.utils.redis_client import RedisClient
from app.utils.kafka_producer import KafkaProducer
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.security.jwt import decode_token
from app.utils.redis_client import is_blacklisted

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    if await is_blacklisted(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token blacklisted")
    return payload


_redis: RedisClient | None = None
_kafka: KafkaProducer | None = None

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_redis() -> RedisClient:
    global _redis
    if _redis is None:
        _redis = RedisClient()
        await _redis.connect()
    return _redis

async def get_kafka() -> KafkaProducer:
    global _kafka
    if _kafka is None:
        _kafka = KafkaProducer()
        await _kafka.start()
    return _kafka