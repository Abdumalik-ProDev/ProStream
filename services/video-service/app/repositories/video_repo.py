from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.video import Video

class VideoRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, video: Video) -> Video:
        self.session.add(video)
        await self.session.commit()
        await self.session.refresh(video)
        return video
    
    async def get(self, video_id: int) -> Optional[Video]:
        q = select(Video).where(Video.id == video_id)
        res = await self.session.execute(q)
        return res.scalars().one_or_none()
    
    async def update(self, video: Video) -> Video:
        self.session.add(video)
        await self.session.commit()
        await self.session.refresh(video)
        return video