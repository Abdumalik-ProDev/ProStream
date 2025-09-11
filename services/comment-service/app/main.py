import asyncio, logging, uvicorn
from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.comments import router as comments_router
from app.core.db import init_db
from app.core.config import settings
from app.grpc.run_server import serve as grpc_serve

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("comment-service")

app = FastAPI(title=settings.APP_NAME)
app.include_router(health_router, prefix="/health")
app.include_router(comments_router)

@app.on_event("startup")
async def on_startup():
    logger.info("init db")
    init_db()
    loop = asyncio.get_running_loop()
    loop.create_task(grpc_serve())

@app.on_event("shutdown")
async def on_shutdown():
    logger.info("shutdown")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)