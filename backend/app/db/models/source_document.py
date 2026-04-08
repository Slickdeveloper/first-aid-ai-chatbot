"""Database model for approved source documents.

This table represents the high-level medical source record that the admin page manages.
Each source can have many searchable chunks.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


PRIMARY_ORGANIZATIONS = ("ifrc", "world health organization", "who")
SUPPORTING_ORGANIZATIONS = ("american red cross", "mayo clinic")


class SourceDocument(Base):
    __tablename__ = "source_documents"

    # Represents a medical source that has been reviewed and approved for retrieval.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    organization: Mapped[str] = mapped_column(String(100), index=True)
    source_url: Mapped[str] = mapped_column(String(500))
    content_path: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text, default="")
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    chunks = relationship(
        "DocumentChunk", back_populates="source_document", cascade="all, delete-orphan"
    )

    @property
    def chunk_count(self) -> int:
        # Helpful computed field for the admin UI.
        return len(self.chunks)

    @property
    def is_searchable(self) -> bool:
        # A source is useful to retrieval only if it is approved and actually chunked.
        return self.is_approved and self.chunk_count > 0

    @property
    def source_tier(self) -> str:
        # Expose the governance tier so the admin UI can explain why some sources are preferred.
        organization = self.organization.lower()

        if any(name in organization for name in PRIMARY_ORGANIZATIONS):
            return "primary"

        if any(name in organization for name in SUPPORTING_ORGANIZATIONS):
            return "supporting"

        return "other"
