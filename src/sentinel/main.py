import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from sqlalchemy import text
from sentinel.config import settings
from sentinel.database import engine
from sentinel.api.jobs import router as jobs_router

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("sentinel")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Sentinel application service...")
    yield
    logger.info("Shutting down Sentinel application service...")
    await engine.dispose()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan
)

# Include API routers
app.include_router(jobs_router)

@app.get("/health", status_code=status.HTTP_200_OK)
@app.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_probe():
    return {"status": "healthy"}

@app.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_probe():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"status": "not_ready", "database": "disconnected"}
