from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    title: str
    filename: str
    file_size_bytes: int
    status: str
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    limit: int


class DocumentTextResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    extracted_text: str
    page_count: int
    extracted_at: datetime