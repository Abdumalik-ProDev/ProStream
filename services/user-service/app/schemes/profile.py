from pydantic import BaseModel, HttpUrl
from typing import Optional

class ProfileCreate(BaseModel):
    user_id: int
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    is_private: Optional[bool] = False

class ProfileUpdate(BaseModel):
    username: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    is_private: Optional[bool] = False

class ProfileRead(BaseModel):
    id: int
    user_id: int
    username: str
    display_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[HttpUrl]
    is_private: bool

model_config = {"from_attributes": True}