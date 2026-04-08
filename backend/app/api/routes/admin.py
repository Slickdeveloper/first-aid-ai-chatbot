"""Admin API routes.

These endpoints power the admin/source-management screen in the frontend.
They are intentionally separated from the public chat route because they can:
- create or update approved source records
- ingest source files into searchable chunks
- approve/unapprove or delete source material
"""

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models.source_document import SourceDocument
from app.db.session import get_db
from app.schemas.admin import (
    ApprovedSourceCreate,
    ApprovedSourceResponse,
    ApprovedSourceUpdate,
)
from app.services.source_ingestion_service import (
    ingest_source_document,
    parse_source_file,
    resolve_content_path,
    validate_managed_content_path,
    write_source_content,
)

router = APIRouter(prefix="/admin/sources", tags=["admin"])


def require_admin_api_key(x_admin_key: str | None = Header(default=None)) -> None:
    # A shared key is enough for a course project demo, while keeping admin tools
    # separate from the public chat experience.
    settings = get_settings()
    if x_admin_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication failed.",
        )


@router.get("", response_model=list[ApprovedSourceResponse])
def list_sources(
    _: None = Depends(require_admin_api_key),
    db: Session = Depends(get_db),
) -> list[SourceDocument]:
    # Return every stored source so the admin UI can show status, tier, and chunk counts.
    return db.query(SourceDocument).order_by(SourceDocument.id.desc()).all()


@router.post("", response_model=ApprovedSourceResponse, status_code=status.HTTP_201_CREATED)
def create_source(
    payload: ApprovedSourceCreate,
    _: None = Depends(require_admin_api_key),
    db: Session = Depends(get_db),
) -> SourceDocument:
    # The admin form sends both metadata and optional raw content.
    # If raw content is present, we write it to disk and immediately ingest it so
    # the chatbot can start retrieving it without a second manual step.
    try:
        normalized_content_path = validate_managed_content_path(payload.content_path)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    source = SourceDocument(
        title=payload.title,
        organization=payload.organization,
        source_url=payload.source_url,
        content_path=normalized_content_path,
        summary=payload.summary,
        is_approved=True,
    )
    db.add(source)

    try:
        db.flush()

        if payload.raw_content.strip():
            # Persist the reviewed content to the canonical source folder first.
            write_source_content(
                title=source.title,
                organization=source.organization,
                source_url=source.source_url,
                summary=source.summary,
                content_path=source.content_path,
                raw_content=payload.raw_content,
            )
            source = ingest_existing_source(source, db)
        else:
            db.commit()
            db.refresh(source)
    except Exception:
        db.rollback()
        raise

    return source


@router.patch("/{source_id}", response_model=ApprovedSourceResponse)
def update_source(
    source_id: int,
    payload: ApprovedSourceUpdate,
    _: None = Depends(require_admin_api_key),
    db: Session = Depends(get_db),
) -> SourceDocument:
    # PATCH lets the frontend update only the fields that changed instead of
    # resending the full source record every time.
    source = db.get(SourceDocument, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found.")

    # Apply only the fields provided by the admin client.
    update_data = payload.model_dump(exclude_unset=True)
    raw_content = update_data.pop("raw_content", None)
    if "content_path" in update_data:
        try:
            update_data["content_path"] = validate_managed_content_path(update_data["content_path"])
        except ValueError as error:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    for field_name, value in update_data.items():
        setattr(source, field_name, value)

    try:
        if raw_content is not None and raw_content.strip():
            # If content itself changed, rewrite the source file and rebuild chunks.
            write_source_content(
                title=source.title,
                organization=source.organization,
                source_url=source.source_url,
                summary=source.summary,
                content_path=source.content_path,
                raw_content=raw_content,
            )
            source = ingest_existing_source(source, db)
        else:
            db.commit()
            db.refresh(source)
    except Exception:
        db.rollback()
        raise

    return source


def ingest_existing_source(source: SourceDocument, db: Session) -> SourceDocument:
    # Reuse one helper so both "create with content" and "manual re-ingest" follow
    # the exact same parsing and chunk-building logic.
    path = resolve_content_path(source.content_path)
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The source content file does not exist yet.",
        )

    _, body = parse_source_file(path)
    return ingest_source_document(db, source, body)


@router.post("/{source_id}/ingest", response_model=ApprovedSourceResponse)
def ingest_source(
    source_id: int,
    _: None = Depends(require_admin_api_key),
    db: Session = Depends(get_db),
) -> SourceDocument:
    # This endpoint is useful after editing a source file outside the admin UI.
    source = db.get(SourceDocument, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found.")

    return ingest_existing_source(source, db)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(
    source_id: int,
    _: None = Depends(require_admin_api_key),
    db: Session = Depends(get_db),
) -> Response:
    # Deleting a source also removes its chunks because the relationship is configured
    # with cascade delete.
    source = db.get(SourceDocument, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found.")

    db.delete(source)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
