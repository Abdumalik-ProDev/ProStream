import os
import tempfile
import shutil
import asyncio
from app.workers.celery_app import celery
from app.utils.s3 import s3_client, make_object_prefix
from app.utils.ffmpeg import transcode_to_hls
from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.services.video_service import VideoService
from app.utils.kafka import publish_event

@celery.task(name="video.process")
def process_video_task(video_id: int):
    """
    Celery worker sync function: downloads object from MinIO, runs ffmpeg, uploads HLS files back to bucket.
    """
    # run inside the worker process (synchronous)
    import boto3
    # Using boto3 for simpler sync ops in workers
    session = boto3.Session(
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
    )
    s3 = session.client("s3", endpoint_url=f"http{'s' if settings.MINIO_SECURE else ''}://{settings.MINIO_ENDPOINT}")

    # locate object key via DB
    import asyncio, sys
    # need to run async DB query inside sync task: use asyncio.run
    async def fetch_and_process():
        async with AsyncSessionLocal() as db:
            svc = VideoService(db)
            video = await svc.get_video(video_id)
            if not video:
                raise RuntimeError("video not found")
            object_key = video.original_object_key
            # prepare temp dir
            tmpdir = tempfile.mkdtemp()
            local_path = os.path.join(tmpdir, os.path.basename(object_key))
            # download
            s3.download_file(settings.MINIO_BUCKET, object_key, local_path)
            # process
            out_dir = os.path.join(tmpdir, "hls")
            os.makedirs(out_dir, exist_ok=True)
            master_path = transcode_to_hls(local_path, out_dir)
            # upload processed files to S3 under prefix videos/{video_id}/hls/
            prefix = f"videos/{video_id}/hls/"
            for root, dirs, files in os.walk(out_dir):
                for fname in files:
                    path = os.path.join(root, fname)
                    key = prefix + os.path.relpath(path, out_dir).replace("\\","/")
                    s3.upload_file(path, settings.MINIO_BUCKET, key)
            # upload thumbnail if produced (skipped here)
            # update DB
            async with AsyncSessionLocal() as db2:
                svc2 = VideoService(db2)
                await svc2.mark_ready(video_id=video_id, processed_prefix=f"videos/{video_id}/hls/", thumbnail_key=None)
            shutil.rmtree(tmpdir)
            await publish_event(settings.KAFKA_TOPIC_VIDEO, "video.processed", {"video_id": video_id})
    asyncio.run(fetch_and_process())