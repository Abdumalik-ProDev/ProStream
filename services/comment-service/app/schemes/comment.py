# app/schemas/comment.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class CommentCreate(BaseModel):
    video_id: str
    parent_id: Optional[str] = None
    content: str = Field(min_length=1, max_length=1000)

class CommentRead(BaseModel):
    id: str
    user_id: str
    video_id: str
    parent_id: Optional[str]
    content: str
    is_deleted: bool
    is_hidden: bool
    like_count: int
    created_at: datetime
    updated_at: Optional[datetime]

class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=1000)
    is_hidden: Optional[bool] = None

class CommentDelete(BaseModel):
    id: str
    is_deleted: bool = True

    class Config:
        orm_mode = True

class CommentList(BaseModel):
    items: List[CommentRead]
    total: int
    limit: int
    offset: int