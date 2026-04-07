from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import handle_chat_message

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def create_chat_response(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    # Accept one chat request and return a grounded, citation-aware answer.
    return handle_chat_message(payload, db)
