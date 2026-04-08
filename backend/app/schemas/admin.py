"""Pydantic schemas for admin/source-management operations.

These schemas validate what the admin page can send to the backend and what it
receives back for display.
"""

from pydantic import BaseModel, ConfigDict, Field


class ApprovedSourceCreate(BaseModel):
    # Used when a new approved source is created from the admin form.
    title: str = Field(min_length=3, max_length=255)
    organization: str = Field(min_length=2, max_length=100)
    source_url: str = Field(min_length=5, max_length=500)
    content_path: str = Field(min_length=1, max_length=255)
    summary: str = Field(default="", max_length=3000)
    raw_content: str = Field(default="", max_length=20000)


class ApprovedSourceUpdate(BaseModel):
    # All fields are optional because PATCH updates only the changed values.
    title: str | None = Field(default=None, min_length=3, max_length=255)
    organization: str | None = Field(default=None, min_length=2, max_length=100)
    source_url: str | None = Field(default=None, min_length=5, max_length=500)
    content_path: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = Field(default=None, max_length=3000)
    raw_content: str | None = Field(default=None, max_length=20000)
    is_approved: bool | None = None


class ApprovedSourceResponse(BaseModel):
    # `from_attributes=True` lets SQLAlchemy model objects be returned directly.
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    organization: str
    source_tier: str
    source_url: str
    content_path: str
    summary: str
    is_approved: bool
    chunk_count: int
    is_searchable: bool
