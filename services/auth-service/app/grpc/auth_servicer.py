import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.grpc import auth_pb2, auth_pb2_grpc
from app.core.db import AsyncSessionLocal
from app.services.auth_service import AuthService
from app.core.metrics import AUTH_EVENTS

logger = logging.getLogger(__name__)

class AuthServicer(auth_pb2_grpc.AuthServiceServicer):
    async def ValidateToken(self, request, context):
        token = request.token
        from app.security.jwt import decode_token
        payload = decode_token(token)
        if not payload:
            return auth_pb2.ValidateReply(valid=False, user_id="", error="invalid")
        jti = payload.get("jti")
        # check blacklist via redis
        from app.utils.redis_client import is_jti_blacklisted
        if jti and await is_jti_blacklisted(jti):
            return auth_pb2.ValidateReply(valid=False, user_id="", error="revoked")
        return auth_pb2.ValidateReply(valid=True, user_id=str(payload.get("sub") or ""), error="")

    async def Login(self, request, context):
        async with AsyncSessionLocal() as session:  # AsyncSessionLocal defined in core/db.py
            svc = AuthService(session)
            class Req: pass
            req = Req()
            req.username = request.username
            req.password = request.password
            res = await svc.authenticate_user(req)
            if not res:
                context.abort(code=5, details="unauthenticated")
            AUTH_EVENTS.labels(event_type="login").inc()
            return auth_pb2.AuthReply(access_token=res["access_token"], refresh_token=res["refresh_token"], expires_at=res["expires_at"])

    async def Register(self, request, context):
        async with AsyncSessionLocal() as session:
            svc = AuthService(session)
            class Req: pass
            req = Req()
            req.username = request.username
            req.email = request.email
            req.password = request.password
            try:
                res = await svc.register_user(req)
            except Exception as e:
                context.abort(code=13, details=str(e))
            AUTH_EVENTS.labels(event_type="register").inc()
            return auth_pb2.AuthReply(access_token=res["access_token"], refresh_token=res["refresh_token"], expires_at=res["expires_at"])