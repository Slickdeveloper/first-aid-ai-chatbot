"""Database model for document chunks.

Chunks are the retrieval unit used by the TF-IDF pipeline. They let the chatbot
return focused citations instead of entire documents.
"""

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    # Stores searchable slices of approved source content with citation metadata.
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_document_id: Mapped[int] = mapped_column(
        ForeignKey("source_documents.id", ondelete="CASCADE"), index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer)
    chunk_text: Mapped[str] = mapped_column(Text)
    citation_label: Mapped[str] = mapped_column(String(255))
    section: Mapped[str] = mapped_column(String(255), default="")

    # ORM relationship back to the parent approved source.
    source_document = relationship("SourceDocument", back_populates="chunks")
