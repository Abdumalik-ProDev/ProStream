from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.profile import UserProfile

class ProfileRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id:int) -> Optional[UserProfile]:
        q = select(UserProfile).where(UserProfile.user_id == user_id)
        res = await self.session.execute(q)
        return res.scalars().one_or_none
    
    async def get_by_username(self, username: str) -> Optional[UserProfile]:
        q = select(UserProfile).where(UserProfile.username == username)
        res = await self.session.execute(q)
        return res.scalars().one_or_none
    
    async def create(self, profile: UserProfile) -> UserProfile:
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
    
    async def update(self, profile: UserProfile) -> UserProfile:
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile