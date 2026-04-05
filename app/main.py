from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.ingest_routes import router as ingest_router
from app.api.review_routes import router as review_router
from app.core.database import ReviewStore
from app.core.dspy_config import configure_dspy
from app.core.logging import configure_logging
from app.core.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    app.state.settings = settings
    app.state.lm = configure_dspy(settings)
    app.state.review_store = ReviewStore(settings.sqlite_db_path, settings.upload_storage_dir)
    app.state.review_store.initialize()
    review_router.store = app.state.review_store
    yield


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(ingest_router)
app.include_router(review_router)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).resolve().parent / "static"),
    name="static",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app_env": settings.app_env,
        "dspy_model": settings.dspy_model_identifier,
        "dspy_api_base": settings.dspy_api_base,
    }


@app.get("/health/db")
def health_db():
    return app.state.review_store.healthcheck()
