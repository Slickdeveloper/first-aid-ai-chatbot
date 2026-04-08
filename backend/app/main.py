"""Main FastAPI application entry point.

This file wires the major backend pieces together:
- configuration loading
- database table creation for local development
- CORS so the React frontend can call the API
- route registration for chat and admin features
- optional startup bootstrapping for deployment

In the overall system, this is the first backend file that runs when `uvicorn` starts.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.admin import router as admin_router
from app.api.routes.chat import router as chat_router
from app.core.config import get_settings
from app.db.models import AuditLog, ChatLog, DocumentChunk, SourceDocument
from app.db.session import Base, SessionLocal, engine
from app.services.source_ingestion_service import ingest_text_file, list_source_files

settings = get_settings()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST_DIR = PROJECT_ROOT / "frontend" / "dist"


def bootstrap_demo_sources() -> None:
    # Demo deployments use SQLite and an ephemeral filesystem, so bootstrapping from
    # the canonical checked-in source files keeps the app usable after each restart.
    if not settings.auto_ingest_sources:
        return

    db = SessionLocal()
    try:
        has_chunks = db.query(DocumentChunk.id).first() is not None
        if has_chunks:
            return

        for source_path in list_source_files():
            ingest_text_file(db, source_path)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Create tables and seed the demo knowledge base before the app starts serving traffic.
    Base.metadata.create_all(bind=engine)
    bootstrap_demo_sources()
    yield


# Create the FastAPI app once using values from environment configuration.
app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Allow the frontend hostnames configured in the environment to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API route groups.
app.include_router(chat_router)
app.include_router(admin_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    # Simple health endpoint used to confirm that the API is alive.
    return {"status": "ok"}


if FRONTEND_DIST_DIR.exists():
    # Production deployments can serve the built frontend from the same public origin
    # as the API, which avoids cross-origin configuration mistakes.
    app.mount("/", StaticFiles(directory=FRONTEND_DIST_DIR, html=True), name="frontend")
