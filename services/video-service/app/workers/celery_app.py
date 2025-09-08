from celery import Celery
from app.core.config import settings

celery = Celery(
    "video_workers",
    broker=settings.CELERY_BROKER,
    backend=settings.CELERY_BACKEND,
)

celery.conf.update(task_serializer="json", accept_content=["json"], result_serializer="json", timezone="UTC", enable_utc=True)

