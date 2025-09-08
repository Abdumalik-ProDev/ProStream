import uvicorn
import logging
import asyncio
from fastapi import FastAPI
from app.api.users import router as users_router
from app.api.health import router as health_router
from app.core.metrics import instrument_fastapi
from app.core.db import init_db
from app.grpc.run_server import serve as grpc_serve
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("user-service")

app = FastAPI(title=settings.APP_NAME)

app.include_router(health_router, prefix="/health")
app.include_router(users_router)

instrument_fastapi(app)

@app.on_event("startup")
async def on_startup():
    logger.info("startup: init db")
    await init_db()
    # start gRPC server in background
    loop = asyncio.get_running_loop()
    loop.create_task(grpc_serve())

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("shutdown")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)