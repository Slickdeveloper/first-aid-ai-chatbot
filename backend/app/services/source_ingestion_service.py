"""Source file ingestion helpers.

This module bridges curated source files on disk and searchable chunks in the database.
It is used by:
- CLI ingestion scripts
- the admin/source-management API
"""

from pathlib import Path

from sqlalchemy.orm import Session

from app.db.models.document_chunk import DocumentChunk
from app.db.models.source_document import SourceDocument
from app.rag.chunking import enumerate_chunks, chunk_text

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_FILES_DIR = PROJECT_ROOT / "data" / "sources"
LEGACY_RAW_SOURCES_DIR = PROJECT_ROOT / "data" / "raw"


def normalize_content_path(content_path: str) -> str:
    # Keep older `data/raw/...` references compatible while the project now uses
    # `data/sources/...` as the canonical location.
    normalized = content_path.replace("\\", "/").strip()

    if normalized.startswith("data/raw/"):
        return "data/sources/" + normalized.removeprefix("data/raw/")

    if normalized.startswith("data/sources/"):
        return normalized

    return normalized


def validate_managed_content_path(content_path: str) -> str:
    # Only allow source files inside the canonical `data/sources/` directory.
    # This prevents the admin API from writing arbitrary files elsewhere on disk.
    normalized = normalize_content_path(content_path)
    path = Path(normalized)

    if path.is_absolute():
        raise ValueError("Content paths must be relative to the project root.")

    normalized_parts = Path(normalized).parts
    if len(normalized_parts) < 3 or normalized_parts[0] != "data" or normalized_parts[1] != "sources":
        raise ValueError("Content paths must be stored under data/sources/.")

    if ".." in normalized_parts:
        raise ValueError("Content paths cannot contain path traversal segments.")

    return str(Path(*normalized_parts)).replace("\\", "/")


def list_source_files() -> list[Path]:
    # Return only real ingestable content files. Documentation files and hidden files
    # are skipped so they do not accidentally become retrieval sources.
    def is_ingestable_file(path: Path) -> bool:
        return (
            path.is_file()
            and path.suffix.lower() in {".md", ".txt"}
            and not path.name.startswith(".")
            and path.name.lower() != "readme.md"
        )

    if SOURCE_FILES_DIR.exists():
        return sorted(path for path in SOURCE_FILES_DIR.iterdir() if is_ingestable_file(path))

    if LEGACY_RAW_SOURCES_DIR.exists():
        return sorted(path for path in LEGACY_RAW_SOURCES_DIR.iterdir() if is_ingestable_file(path))

    return []


def parse_source_file(path: Path) -> tuple[dict[str, str], str]:
    # Support a simple metadata header so local files can point back to official
    # source pages.
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    metadata: dict[str, str] = {}
    body_start = 0

    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            body_start = index + 1
            break

        # The header ends as soon as a line no longer looks like `Key: Value`.
        if ":" not in stripped:
            break

        key, value = stripped.split(":", 1)
        normalized_key = key.strip().lower()
        if normalized_key in {"title", "organization", "source url", "summary"}:
            metadata[normalized_key] = value.strip()
            body_start = index + 1
        else:
            break

    body = "\n".join(lines[body_start:]).strip()
    return metadata, body


def build_source_file_content(
    title: str, organization: str, source_url: str, summary: str, raw_content: str
) -> str:
    # Write source files in one consistent format so both humans and ingestion code
    # can read them easily.
    header_lines = [
        f"Title: {title}",
        f"Organization: {organization}",
        f"Source URL: {source_url}",
        f"Summary: {summary}",
        "",
    ]
    return "\n".join(header_lines) + raw_content.strip() + "\n"


def resolve_content_path(content_path: str) -> Path:
    # Resolve relative project paths first, then fall back to legacy paths when needed.
    normalized = normalize_content_path(content_path)
    path = Path(normalized)
    if path.is_absolute():
        return path

    resolved = (PROJECT_ROOT / normalized).resolve()
    if resolved.exists():
        return resolved

    legacy_normalized = normalized.replace("data/sources/", "data/raw/", 1)
    legacy_resolved = (PROJECT_ROOT / legacy_normalized).resolve()
    if legacy_resolved.exists():
        return legacy_resolved

    return resolved


def write_source_content(
    title: str,
    organization: str,
    source_url: str,
    summary: str,
    content_path: str,
    raw_content: str,
) -> Path:
    # Persist the admin-approved source text to disk before chunking it into the database.
    destination = resolve_content_path(validate_managed_content_path(content_path))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        build_source_file_content(title, organization, source_url, summary, raw_content),
        encoding="utf-8",
    )
    return destination


def ingest_source_document(db: Session, source: SourceDocument, body: str) -> SourceDocument:
    # Rebuild all chunks for a source so retrieval always reflects the latest
    # approved content.
    db.query(DocumentChunk).filter(DocumentChunk.source_document_id == source.id).delete()

    for index, chunk in enumerate_chunks(chunk_text(body)):
        # Each chunk becomes one searchable record tied back to its parent source.
        db.add(
            DocumentChunk(
                source_document_id=source.id,
                chunk_index=index,
                chunk_text=chunk,
                citation_label=f"Chunk {index + 1}",
                section="Imported text",
            )
        )

    db.commit()
    db.refresh(source)
    return source


def ingest_text_file(db: Session, path: Path) -> SourceDocument:
    # Create or update one approved source record and its searchable chunks from a
    # local text file.
    metadata, body = parse_source_file(path)
    normalized_content_path = normalize_content_path(str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"))
    legacy_content_path = normalized_content_path.replace("data/sources/", "data/raw/", 1)

    # Match both new and old content paths so existing database rows continue to work
    # after the project-folder cleanup.
    source = (
        db.query(SourceDocument)
        .filter(SourceDocument.content_path.in_([normalized_content_path, legacy_content_path, str(path)]))
        .first()
    )

    title = metadata.get("title", path.stem.replace("_", " ").title())
    organization = metadata.get("organization", "Local Approved Source")
    source_url = metadata.get("source url", path.as_uri())
    summary = metadata.get("summary", "Imported from the local canonical source directory.")

    if source is None:
        source = SourceDocument(
            title=title,
            organization=organization,
            source_url=source_url,
            content_path=normalized_content_path,
            summary=summary,
            is_approved=True,
        )
        db.add(source)
        db.flush()
    else:
        # Existing rows are updated in place so source IDs remain stable.
        source.title = title
        source.organization = organization
        source.source_url = source_url
        source.content_path = normalized_content_path
        source.summary = summary
        source.is_approved = True

    return ingest_source_document(db, source, body)
