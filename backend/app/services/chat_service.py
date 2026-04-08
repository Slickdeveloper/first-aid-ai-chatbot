"""Chat orchestration service.

This module coordinates the full request lifecycle:
frontend question -> retrieval -> safety check -> answer generation -> optional logging.
"""

import json

from sqlalchemy.orm import Session

from app.db.models.chat_log import ChatLog
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import generate_grounded_answer
from app.services.retrieval_service import retrieve_approved_content
from app.services.safety_service import (
    build_disclaimer,
    build_emergency_action,
    is_emergency,
)


def handle_chat_message(payload: ChatRequest, db: Session | None = None) -> ChatResponse:
    # The chat flow is retrieval first: gather citations, run safety checks, then form an answer.
    # This design is safer than asking a language model to answer from memory.
    retrieval = retrieve_approved_content(payload.message, db)
    emergency = is_emergency(payload.message)
    answer = generate_grounded_answer(
        payload.message,
        retrieval.citations,
        retrieval.supporting_passages,
        emergency,
    )

    response = ChatResponse(
        answer=answer,
        citations=retrieval.citations,
        disclaimer=build_disclaimer(),
        emergency=emergency,
        recommended_action=build_emergency_action() if emergency else None,
    )

    if db is not None:
        # Persist the interaction so the project can support audits and later evaluation.
        # Citations are stored as JSON text to keep the logging table simple.
        chat_log = ChatLog(
            session_id=payload.session_id,
            user_message=payload.message,
            assistant_message=response.answer,
            citations_json=json.dumps([citation.model_dump() for citation in retrieval.citations]),
            status="emergency" if emergency else "answered",
        )
        db.add(chat_log)
        db.commit()

    return response
