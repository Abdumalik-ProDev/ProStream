import uuid, os
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.video_repo import VideoRepo
from app.models.video import Video
from app.utils.s3 import generate_presigned_put, make_object_prefix
from app.core.config import settings
from app.utils.kafka import publish_event

class VideoService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = VideoRepo(session)

    async def init_upload(self, owner_user_id: int, filename: str, title: str, description: str | None, content_type: str):
        upload_id = str(uuid.uuid4())
        object_key = f"uploads/{upload_id}/{filename}"
        presigned = await generate_presigned_put(object_key=object_key, expires_in=3600)
        video = Video(owner_user_id=owner_user_id, title=title, description=description, original_object_key=object_key, status="uploaded")
        created = await self.repo.create(video)
        await publish_event(settings.kafka_topic_video, "video.upload_initiated", {"video_id": created.id, "upload_id": upload_id})
        return {"video_id": created.id, "upload_id": upload_id, "presigned_url": presigned}
    
    async def mark_processing(self, video_id: int, processed_prefix: str, thumbnail_key: str | None = None):
        video = await self.repo.get(video_id)
        if not video:
            raise ValueError("video not found")
        video.status = "processing"
        video.processed_prefix = processed_prefix
        video.thumbnail_key = thumbnail_key
        video.updated_at = datetime.utcnow()
        return await self.repo.update(video)
    
    async def mark_ready(self, video_id: int, processed_prefix: str, thumbnail_key: str | None = None):
        video = await self.repo.get(video_id)
        if not video:
            raise ValueError("video not found")
        video.status = "ready"
        video.processed_prefix = processed_prefix
        video.thumbnail_key = thumbnail_key
        video.updated_at = datetime.utcnow()
        v = await self.repo.update(video)
        await publish_event(settings.kafka_topic_video, "video.processed", {"video_id": video_id})
        return v