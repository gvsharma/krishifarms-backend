from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.schemas.common import ORMModel, PaginatedResponse


class PresignUploadRequest(BaseModel):
    document_type: str = Field(min_length=2, max_length=50)
    file_name: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(min_length=3, max_length=100)
    file_size_bytes: int = Field(gt=0, le=26214400)


class PresignUploadResponse(BaseModel):
    upload_url: str
    object_key: str
    bucket: str


class DocumentCreateRequest(BaseModel):
    document_type: str
    file_name: str
    mime_type: str
    file_size_bytes: int = Field(gt=0)
    object_key: str
    checksum_sha256: str | None = None
    metadata: dict = Field(default_factory=dict)


class DocumentLinkRequest(BaseModel):
    entity_type: str
    entity_id: UUID
    link_role: str = "primary_attachment"


class DocumentResponse(ORMModel):
    id: UUID
    org_id: UUID
    document_type: str
    file_name: str
    mime_type: str
    file_size_bytes: int
    s3_bucket: str
    s3_key: str
    checksum_sha256: str | None = None
    metadata: dict
    uploaded_by: UUID | None = None
    created_at: datetime
    updated_at: datetime


class DocumentDownloadResponse(BaseModel):
    download_url: str


class DocumentListResponse(PaginatedResponse[DocumentResponse]):
    pass
