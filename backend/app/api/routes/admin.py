from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.models.source_document import SourceDocument
from app.db.session import get_db
from app.schemas.admin import ApprovedSourceCreate, ApprovedSourceResponse

router = APIRouter(prefix="/admin/sources", tags=["admin"])


@router.get("", response_model=list[ApprovedSourceResponse])
def list_sources(db: Session = Depends(get_db)) -> list[SourceDocument]:
    # Returns all approved-source records for admin review screens.
    return db.query(SourceDocument).order_by(SourceDocument.id.desc()).all()


@router.post("", response_model=ApprovedSourceResponse, status_code=status.HTTP_201_CREATED)
def create_source(
    payload: ApprovedSourceCreate, db: Session = Depends(get_db)
) -> SourceDocument:
    # Starter flow: every created source is marked approved immediately.
    source = SourceDocument(**payload.model_dump(), is_approved=True)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source
