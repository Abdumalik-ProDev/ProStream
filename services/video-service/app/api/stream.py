from fastapi import APIRouter, Depends, HTTPException
from app.core.db import AsyncSessionLocal
from app.services.video_service import VideoService
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.s3 import generate_presigned_get

router = APIRouter(prefix="/stream", tags=["stream"])

async def get_session() -> AsyncSession: # pyright: ignore[reportInvalidTypeForm]
    async with AsyncSessionLocal() as s:
        yield s

@router.get("/{video_id}")
async def get_stream(video_id: int, session: AsyncSession = Depends(get_session)):
    svc = VideoService(session)
    video = await svc.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="video not found")
    if video.status != "ready":
        raise HTTPException(status_code=400, detail="video not ready")
    # processed_prefix typically: videos/{id}/hls/
    # master playlist key: processed_prefix + "master.m3u8"
    key = f"{video.processed_prefix}master.m3u8"
    url = await generate_presigned_get(key, expires_in=3600)
    return {"playlist_url": url}