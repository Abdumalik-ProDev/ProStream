from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refresh_token import RefreshToken
from datetime import datetime

class RefreshTokenRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, token_obj: RefreshToken) -> RefreshToken:
        self.session.add(token_obj)
        await self.session.commit()
        await self.session.refresh(token_obj)
        return token_obj

    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        q = select(RefreshToken).where(RefreshToken.token == token)
        res = await self.session.execute(q)
        return res.scalars().one_or_none()

    async def revoke(self, token_obj: RefreshToken):
        token_obj.expires_at = datetime.utcnow()
        await self.session.commit()
        return token_obj