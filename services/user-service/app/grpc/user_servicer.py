from app.grpc import user_pb2, user_pb2_grpc
from app.core.db import AsyncSessionLocal
from app.services.profile_service import ProfileService

class UserServicer(user_pb2_grpc.UserServiceServicer):
    async def GetProfile(self, request, context):
        # verify token and extract sub
        from app.security.jwt import verify_jwt
        payload = verify_jwt(request.token)
        if not payload:
            context.abort(16, "unauthenticated")
        user_id = int(payload.get("sub"))
        async with AsyncSessionLocal() as session:
            service = ProfileService(session)
            prof = await service.get_profile_by_user_id(user_id)
            if not prof:
                context.abort(5, "not found")
            return user_pb2.ProfileReply(
                id=prof.id,
                user_id=prof.user_id,
                username=prof.username,
                display_name=prof.display_name or "",
                bio=prof.bio or "",
                avatar_url=prof.avatar_url or "",
                is_private=prof.is_private
            )

    async def GetProfileByUserId(self, request, context):
        async with AsyncSessionLocal() as session:
            service = ProfileService(session)
            prof = await service.get_profile_by_user_id(request.user_id)
            if not prof:
                context.abort(5, "not found")
            return user_pb2.ProfileReply(
                id=prof.id,
                user_id=prof.user_id,
                username=prof.username,
                display_name=prof.display_name or "",
                bio=prof.bio or "",
                avatar_url=prof.avatar_url or "",
                is_private=prof.is_private
            )
        
    async def GetProfileByUsername(self, request, context):
        async with AsyncSessionLocal() as session:
            service = ProfileService(session)
            prof = await service.get_profile_by_username(request.username)
            if not prof:
                context.abort(5, "not found")
            return user_pb2.ProfileReply(
                id=prof.id,
                user_id=prof.user_id,
                username=prof.username,
                display_name=prof.display_name or "",
                bio=prof.bio or "",
                avatar_url=prof.avatar_url or "",
                is_private=prof.is_private
            )