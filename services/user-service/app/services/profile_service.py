from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.profile_repo import ProfileRepo
from app.models.profile import UserProfile
from app.schemes.profile import ProfileCreate, ProfileRead, ProfileUpdate
from app.utils.kafka import publish_event
from app.core.config import settings

class ProfileService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ProfileRepo(session)

    async def create_profile(self, payload: ProfileCreate):
        exist = await self.repo.get_by_user_id(payload.user_id)or self.repo.get_by_username(payload.username)
        if exist:
            raise ValueError("Profile with this id or username is alredy exists")
        profile = UserProfile(
            user_id=payload.user_id,
            username=payload.username,
            display_name=payload.display_name,
            bio=payload.bio,
            avatar_url=str(payload.avatar_url) if payload.avatar_url else None,
            is_private=payload.is_private
        )
        created = await self.repo.create(profile)
        await publish_event(settings.kafka_topic_user, "user.profile.created", {"user_id": created.user_id, "username": created.username})
        return created
    
    async def get_profile_by_user_id(self, user_id: int):
        return await self.repo.get_by_user_id(user_id)
    
    async def get_profile_by_username(self, username: str):
        return await self.repo.get_by_username(username)
    
    async def update_profile(self, user_id: int, username: str, payload: ProfileUpdate):
        prof = await self.repo.get_by_user_id(user_id) or self.repo.get_by_username(username)
        if not prof:
            raise ValueError("Profile not found")
        if payload.display_name is not None:
            prof.display_name = payload.display_name
        if payload.bio is not None:
            prof.bio = payload.bio
        if payload.avatar_url is not None:
            prof.avatar_url = str(payload.avatar_url)
        if payload.is_private is not None:
            prof.is_private = payload.is_private
        payload.updated_at = __import__("datetime").datetime.utcnow()
        return await self.repo.update(prof)