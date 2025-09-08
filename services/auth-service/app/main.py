import uvicorn
import asyncio
import logging
from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.core.metrics import instrument_fastapi
from app.core.db import init_db
from app.grpc.run_server import serve as grpc_serve
from app.api.routes.dependencies import oauth2_scheme

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Auth Service")

app.include_router(health_router, prefix="/health")
app.include_router(auth_router, prefix="/auth")

instrument_fastapi(app)

@app.on_event("startup")
async def startup():
    logger.info("starting up: init db and spawn grpc server")
    await init_db()
    loop = asyncio.get_running_loop()
    loop.create_task(grpc_serve())

@app.on_event("shutdown")
async def shutdown():
    logger.info("shutting down")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)