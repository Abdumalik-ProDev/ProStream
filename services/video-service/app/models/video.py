from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class Video(SQLModel, table=True):
    __tablename__= "videos"
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_user_id: int = Field(index=True, nullable=False)
    title: str
    description: Optional[str] = None
    original_object_key: str
    processed_prefix: Optional[str] = None
    thumbnail_key: Optional[str] = None
    status: str = Field(default="upload")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None