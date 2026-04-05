from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.ingest_routes import router as ingest_router
from app.core.dspy_config import configure_dspy
from app.core.logging import configure_logging
from app.core.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    app.state.settings = settings
    app.state.lm = configure_dspy(settings)
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(ingest_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app_env": settings.app_env,
        "dspy_model": settings.dspy_model_identifier,
        "dspy_api_base": settings.dspy_api_base,
    }
