from pydantic import BaseModel, Field


class ApprovedSourceCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    organization: str = Field(min_length=2, max_length=100)
    source_url: str = Field(min_length=5, max_length=500)
    content_path: str = Field(min_length=1, max_length=255)
    summary: str = Field(default="", max_length=3000)


class ApprovedSourceResponse(BaseModel):
    id: int
    title: str
    organization: str
    source_url: str
    content_path: str
    summary: str
    is_approved: bool
