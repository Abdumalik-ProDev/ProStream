from pydantic import BaseModel, HttpUrl
from typing import Optional

class UploadInitRequest(BaseModel):
    filename: str
    content_type: str
    owner_user_id: int
    title: str
    description: Optional[str] = None

class UploadInitResponse(BaseModel):
    upload_id: str
    presigned_urls: dict

class VideoRead(BaseModel):
    id: int
    owner_user_id: int
    title: str
    description: Optional[str]
    status: str
    playlist_url: Optional[HttpUrl]

    model_config = {"from_attributes": True}