# app/services/auth_service.py
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository
from app.repositories.refresh_repo import RefreshTokenRepository
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.security.hash import hash_password, verify_password
from app.security.jwt import create_access_token, decode_token
from app.utils.kafka_producer import publish_event
from app.utils.redis_client import blacklist_jti
from app.core.config import settings
from datetime import datetime

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.refresh_repo = RefreshTokenRepository(session)
        self.kafka_topic = getattr(settings, "KAFKA_TOPIC_AUTH", "auth-events")

    async def register_user(self, user_create) -> Dict[str, Any]:
        # user_create: pydantic model with username, email, password
        existing = await self.user_repo.get_by_username(user_create.username)
        if existing:
            raise ValueError("username taken")
        hashed = hash_password(user_create.password)
        user = User(username=user_create.username, email=user_create.email, hashed_password=hashed)
        created = await self.user_repo.create(user)
        await publish_event(self.kafka_topic, "user.created", {"user_id": created.id, "email": created.email})
        token_info = create_access_token(str(created.id))
        # create refresh token row:
        refresh_raw = __import__("secrets").token_urlsafe(48)
        expires_at = datetime.utcnow() + __import__("datetime").timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        rt = RefreshToken(user_id=created.id, token=refresh_raw, expires_at=expires_at)
        await self.refresh_repo.create(rt)
        return {"access_token": token_info["access_token"], "refresh_token": refresh_raw, "expires_at": token_info["expires_at"]}

    async def authenticate_user(self, user_login) -> Optional[Dict[str, Any]]:
        # user_login: pydantic model with username/password
        user = await self.user_repo.get_by_username(user_login.username)
        if not user:
            return None
        if not verify_password(user_login.password, user.hashed_password):
            await publish_event(self.kafka_topic, "user.login_failed", {"username": user_login.username})
            return None
        token_info = create_access_token(str(user.id))
        refresh_raw = __import__("secrets").token_urlsafe(48)
        expires_at = datetime.utcnow() + __import__("datetime").timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        rt = RefreshToken(user_id=user.id, token=refresh_raw, expires_at=expires_at)
        await self.refresh_repo.create(rt)
        await publish_event(self.kafka_topic, "user.logged_in", {"user_id": user.id})
        return {"access_token": token_info["access_token"], "refresh_token": refresh_raw, "expires_at": token_info["expires_at"]}

    async def refresh_token(self, refresh_raw: str) -> Optional[Dict[str, Any]]:
        rt = await self.refresh_repo.get_by_token(refresh_raw)
        if not rt:
            return None
        if rt.expires_at < datetime.utcnow():
            return None
        # revoke old and issue new
        await self.refresh_repo.revoke(rt)
        access = create_access_token(str(rt.user_id))
        new_refresh = __import__("secrets").token_urlsafe(48)
        expires_at = datetime.utcnow() + __import__("datetime").timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        new_rt = RefreshToken(user_id=rt.user_id, token=new_refresh, expires_at=expires_at)
        await self.refresh_repo.create(new_rt)
        await publish_event(self.kafka_topic, "token.refreshed", {"user_id": rt.user_id})
        return {"access_token": access["access_token"], "refresh_token": new_refresh, "expires_at": access["expires_at"]}

    async def revoke_refresh(self, refresh_raw: str) -> bool:
        rt = await self.refresh_repo.get_by_token(refresh_raw)
        if not rt:
            return False
        await self.refresh_repo.revoke(rt)
        await publish_event(self.kafka_topic, "token.revoked", {"user_id": rt.user_id})
        return True

    async def revoke_access(self, jti: str, ttl_seconds: int = 3600*24):
        # blacklist jti in redis
        await blacklist_jti(jti, ttl_seconds)
        await publish_event(self.kafka_topic, "access.revoked", {"jti": jti})