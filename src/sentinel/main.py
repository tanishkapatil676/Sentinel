from fastapi import FastAPI

from sentinel.api.jobs import router as jobs_router

app = FastAPI(
    title="Sentinel Asynchronous Job Processor",
    version="0.1.0",
)

app.include_router(jobs_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
