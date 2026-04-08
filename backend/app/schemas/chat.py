"""Pydantic schemas for chat requests and responses.

These schemas define the contract between frontend and backend, which makes the
data flow easier to validate and explain.
"""

from pydantic import BaseModel, Field


class Citation(BaseModel):
    # Each citation points the UI back to the approved source used for the answer.
    title: str
    organization: str
    url: str
    excerpt: str


class RetrievalResult(BaseModel):
    # Internal shape returned by retrieval before the final answer is generated.
    citations: list[Citation]
    supporting_passages: list[str]


class ChatRequest(BaseModel):
    # Validation here protects the backend from empty or extremely large requests.
    session_id: str = Field(min_length=3, max_length=64)
    message: str = Field(min_length=2, max_length=2000)


class ChatResponse(BaseModel):
    # This matches what the frontend expects to render after each question.
    answer: str
    citations: list[Citation]
    disclaimer: str
    emergency: bool = False
    recommended_action: str | None = None
