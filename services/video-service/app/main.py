import uvicorn, logging
from fastapi import FastAPI
from app.api.upload import router as upload_router
from app.api.stream import router as stream_router
from app.api.health import router as health_router
from app.core.metrics import instrument_fastapi
from app.core.db import init_db
from app.utils.s3 import ensure_bucket
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("video-service")

app = FastAPI(title=settings.app_name)

app.include_router(health_router, prefix="/health")
app.include_router(upload_router)
app.include_router(stream_router)

instrument_fastapi(app)

@app.on_event("startup")
async def startup():
    logger.info("startup: init db and s3 bucket")
    await init_db()
    await ensure_bucket()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)