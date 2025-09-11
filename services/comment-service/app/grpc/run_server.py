import asyncio
from grpc import aio
from app.grpc.comment_servicer import CommentServicer
from app.grpc import comment_pb2_grpc
from app.grpc.interceptor import AuthInterceptor
from app.core.config import settings

async def serve():
    server = aio.server(interceptors=[AuthInterceptor()])
    comment_pb2_grpc.add_CommentServiceServicer_to_server(CommentServicer(), server)
    server.add_insecure_port(f"[::]:{settings.GRPC_PORT}")
    await server.start()
    await server.wait_for_termination()