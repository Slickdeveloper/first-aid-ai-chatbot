from pydantic import BaseModel, Field


class Citation(BaseModel):
    title: str
    organization: str
    url: str
    excerpt: str


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=3, max_length=64)
    message: str = Field(min_length=2, max_length=2000)


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    disclaimer: str
    emergency: bool = False
    recommended_action: str | None = None
