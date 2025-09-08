import asyncio
import logging
from app.grpc.run_server import serve as grpc_serve

logger = logging.getLogger(__name__)

async def start_grpc(loop):
    loop.create_task(grpc_serve())