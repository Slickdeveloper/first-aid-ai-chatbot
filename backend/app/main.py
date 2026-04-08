"""Main FastAPI application entry point.

This file wires the major backend pieces together:
- configuration loading
- database table creation for local development
- CORS so the React frontend can call the API
- route registration for chat and admin features

In the overall system, this is the first backend file that runs when `uvicorn` starts.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.admin import router as admin_router
from app.api.routes.chat import router as chat_router
from app.core.config import get_settings
from app.db.models import AuditLog, ChatLog, DocumentChunk, SourceDocument
from app.db.session import Base, engine

settings = get_settings()
# Create the FastAPI app once using values from environment configuration.
app = FastAPI(title=settings.app_name)
# Create local tables automatically for the starter project.
Base.metadata.create_all(bind=engine)

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
