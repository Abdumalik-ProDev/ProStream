import secrets
from datetime import datetime, timedelta
from app.core.config import settings
from app.utils.redis_client import redis_client

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)

def refresh_expires_at() -> datetime:
    return datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)