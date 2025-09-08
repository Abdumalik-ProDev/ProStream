import aioboto3
from typing import Optional
from app.core.config import settings
from urllib.parse import urljoin

_session = None

def s3_client():
    # Create a session per use (aioboto3 recommended pattern)
    return aioboto3.Session().client(
        "s3",
        endpoint_url=f"http{'s' if settings.MINIO_SECURE else ''}://{settings.MINIO_ENDPOINT}",
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        region_name="us-east-1",
    )

async def ensure_bucket():
    async with s3_client() as client:
        buckets = await client.list_buckets()
        names = [b["Name"] for b in buckets.get("Buckets", [])]
        if settings.MINIO_BUCKET not in names:
            await client.create_bucket(Bucket=settings.MINIO_BUCKET)

async def generate_presigned_put(object_key: str, expires_in: int = 3600) -> str:
    async with s3_client() as client:
        url = await client.generate_presigned_url(
            "put_object",
            Params={"Bucket": settings.MINIO_BUCKET, "Key": object_key},
            ExpiresIn=expires_in,
        )
        return url

async def generate_presigned_get(object_key: str, expires_in: int = 3600) -> str:
    async with s3_client() as client:
        url = await client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.MINIO_BUCKET, "Key": object_key},
            ExpiresIn=expires_in,
        )
        return url

def make_object_prefix(video_id: int) -> str:
    return f"videos/{video_id}/"