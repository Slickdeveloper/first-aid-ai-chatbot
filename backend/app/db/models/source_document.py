from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class SourceDocument(Base):
    __tablename__ = "source_documents"

    # Represents a medical source that has been reviewed and approved for retrieval.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    organization: Mapped[str] = mapped_column(String(100), index=True)
    source_url: Mapped[str] = mapped_column(String(500), unique=True)
    content_path: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text, default="")
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
