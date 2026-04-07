from fastapi import FastAPI

from app.api.routes.admin import router as admin_router
from app.api.routes.chat import router as chat_router
from app.core.config import get_settings
from app.db.session import Base, engine

settings = get_settings()
app = FastAPI(title=settings.app_name)
# Create local tables automatically for the starter project.
Base.metadata.create_all(bind=engine)

# Register API route groups.
app.include_router(chat_router)
app.include_router(admin_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
