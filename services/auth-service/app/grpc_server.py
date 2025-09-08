import asyncio
import logging
from app.grpc.run_server import serve as grpc_serve

logger = logging.getLogger(__name__)

def start_grpc_in_background(loop):
    loop.create_task(grpc_serve())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(grpc_serve())