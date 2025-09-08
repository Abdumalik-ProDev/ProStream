import asyncio
import logging
from grpc import aio
from app.grpc.auth_pb2_grpc import add_AuthServiceServicer_to_server
from app.grpc.auth_servicer import AuthServicer
from app.grpc.interceptor import PrometheusGrpcInterceptor
from app.core.config import settings

logger = logging.getLogger(__name__)

async def serve(host: str = "0.0.0.0", port: int | None = None):
    port = port or settings.GRPC_PORT
    server = aio.server(interceptors=[PrometheusGrpcInterceptor()])
    add_AuthServiceServicer_to_server(AuthServicer(), server)
    server.add_insecure_port(f"{host}:{port}")
    logger.info("gRPC server listening on %s:%s", host, port)
    await server.start()
    await server.wait_for_termination()