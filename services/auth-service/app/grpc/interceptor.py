import logging
from grpc import aio
from app.security.jwt import decode_token
from app.core.metrics import GRPC_REQUESTS, GRPC_LATENCY

logger = logging.getLogger(__name__)

class PrometheusGrpcInterceptor(aio.ServerInterceptor):
    async def intercept_service(self, continuation, handler_call_details):
        handler = await continuation(handler_call_details)
        if handler is None:
            return None
        method = handler_call_details.method or "unknown"
        # unary-unary
        if handler.unary_unary:
            orig = handler.unary_unary
            async def wrapper(request, context):
                GRPC_REQUESTS.labels(rpc_method=method).inc()
                with GRPC_LATENCY.labels(rpc_method=method).time():
                    # check metadata for authorization
                    md = dict(context.invocation_metadata() or [])
                    token = md.get("authorization") or md.get("Authorization")
                    if not token or not decode_token(token):
                        context.abort(code=aio.StatusCode.UNAUTHENTICATED, details="invalid token")
                    return await orig(request, context)
            return aio.unary_unary_rpc_method_handler(
                wrapper,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )
        return handler