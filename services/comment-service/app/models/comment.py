from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
import uuid

class Comment(SQLModel, table=True):

    __tablename__ = "comments"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, index=True)
    user_id: str = Field(index=True, nullable=False)
    video_id: str = Field(index=True, nullable=False)
    parent_id: Optional[str] = Field(default=None, index=True)
    content: str
    is_deleted: bool = False
    is_hidden: bool = False
    like_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None