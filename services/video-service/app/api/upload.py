from fastapi import APIRouter, Depends, HTTPException, status
from app.schemes.video import UploadInitRequest, UploadInitResponse
from app.core.db import AsyncSessionLocal
from app.services.video_service import VideoService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/upload", tags=["upload"])

async def get_session() -> AsyncSession: # pyright: ignore[reportInvalidTypeForm]
    async with AsyncSessionLocal() as s:
        yield s

@router.post("/init", response_model=dict, status_code=status.HTTP_201_CREATED)
async def init_upload(payload: UploadInitRequest, session: AsyncSession = Depends(get_session)):
    svc = VideoService(session)
    res = await svc.init_upload(owner_user_id=payload.owner_user_id, filename=payload.filename, title=payload.title, description=payload.description, content_type=payload.content_type)
    return res

@router.post("/complete/{video_id}", status_code=status.HTTP_202_ACCEPTED)
async def notify_upload_complete(video_id: int, session: AsyncSession = Depends(get_session)):
    """
    Called by client after successful PUT to presigned URL.
    Triggers worker via Kafka event or direct celery task.
    """
    # For simplicity publish event here via Kafka (worker listens)
    from app.utils.kafka import publish_event
    await publish_event("video-events", "upload.completed", {"video_id": video_id})
    return {"status": "ok"}