from grpc import aio
from jose import jwt, JWTError
from app.core.config import settings

class AuthInterceptor(aio.ServerInterceptor):
    async def intercept_service(self, continuation, handler_call_details):
        handler = await continuation(handler_call_details)
        if handler is None:
            return None
        if handler.unary_unary:
            orig = handler.unary_unary
            async def wrapper(request, context):
                md = dict(handler_call_details.invocation_metadata or [])
                token = md.get("authorization") or md.get("Authorization") or ""
                if token:
                    try:
                        jwt.decode(token, settings.AUTH_SERVICE_JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
                    except JWTError:
                        context.abort(aio.StatusCode.UNAUTHENTICATED, "invalid token")
                return await orig(request, context)
            return aio.unary_unary_rpc_method_handler(
                wrapper,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        return handler