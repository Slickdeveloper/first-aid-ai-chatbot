"""Chat API routes.

These routes are the public backend entry point used by the React chat page.
The frontend sends a question here, and the backend returns:
- a grounded answer
- source citations
- disclaimer text
- emergency flags when relevant
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import handle_chat_message

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def create_chat_response(payload: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    # Request body:
    # - session_id: lightweight identifier for grouping chat history
    # - message: the user's first-aid question
    #
    # Response body:
    # - answer: grounded response text
    # - citations: approved sources used to support the answer
    # - disclaimer/emergency metadata used by the frontend
    return handle_chat_message(payload, db)
