import asyncio
from grpc import aio
from app.grpc.user_pb2_grpc import add_UserServiceServicer_to_server
from app.grpc.user_servicer import UserServicer
from app.grpc.interceptor import AuthInterceptor
from app.core.config import settings

async def serve(host="0.0.0.0", port=None):
    port = port or settings.GRPC_PORT
    server = aio.server(interceptors=[AuthInterceptor()])
    add_UserServiceServicer_to_server(UserServicer(), server)
    server.add_insecure_port(f"{host}:{port}")
    await server.start()
    await server.wait_for_termination()