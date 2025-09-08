from grpc import aio
from app.security.jwt import verify_jwt
from app.core.metrics import GRPC_REQUESTS, GRPC_LATENCY

class AuthInterceptor(aio.ServerInterceptor):
    async def intercept_service(self, continuation, handler_call_details):
        handler = await continuation(handler_call_details)
        if handler is None:
            return None
        method = handler_call_details.method or "unknown"
        if handler.unary_unary:
            orig = handler.unary_unary
            async def wrapper(request, context):
                GRPC_REQUESTS.labels(rpc_method=method).inc()
                with GRPC_LATENCY.labels(rpc_method=method).time():
                    md = dict(context.invocation_metadata() or [])
                    token = md.get("authorization") or md.get("Authorization") or ""
                    if not token or not verify_jwt(token):
                        context.abort(aio.StatusCode.UNAUTHENTICATED, "invalid token")
                    return await orig(request, context)
            return aio.unary_unary_rpc_method_handler(
                wrapper,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        return handler