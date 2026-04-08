"""CLI entry point for loading approved first-aid sources into the retrieval pipeline.

This script reads canonical approved source files from `data/sources/`, then
creates or updates searchable source records and chunks in the database.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"

if str(BACKEND_ROOT) not in sys.path:
    # Allow this script to be run from the repository root without extra PYTHONPATH setup.
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.models.document_chunk import DocumentChunk
from app.db.models.source_document import SourceDocument
from app.db.session import SessionLocal
from app.services.source_ingestion_service import ingest_text_file, list_source_files


if __name__ == "__main__":
    # Iterate over the canonical source directory and ingest only text-like files.
    for source in list_source_files():
        if source.suffix.lower() in {".txt", ".md"}:
            db = SessionLocal()
            try:
                ingest_text_file(db, source)
                print(f"Ingested {source.name}")
            finally:
                db.close()
        else:
            print(f"Skipped {source.name}: unsupported file type")
