from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUserContext, get_db, require_permission
from app.modules.documents import service
from app.modules.documents.schemas import (
    DocumentCreateRequest,
    DocumentDownloadResponse,
    DocumentLinkRequest,
    DocumentListResponse,
    DocumentResponse,
    PresignUploadRequest,
    PresignUploadResponse,
)
from app.shared.schemas.common import APIResponse, MessageResponse
from app.shared.services.s3 import S3Service, get_s3_service

router = APIRouter(prefix="/documents", tags=["Documents"])


def _serialize_document(document) -> DocumentResponse:
    data = DocumentResponse.model_validate(document)
    return data.model_copy(update={"metadata": document.metadata_})


@router.post("/presign-upload", response_model=APIResponse[PresignUploadResponse])
def presign_upload(
    payload: PresignUploadRequest,
    ctx: CurrentUserContext = Depends(require_permission("documents:create")),
    db: Session = Depends(get_db),
    s3: S3Service = Depends(get_s3_service),
):
    result = service.presign_upload(db, ctx.user.org_id, payload, s3)
    return APIResponse(data=PresignUploadResponse(**result))


@router.post("", response_model=APIResponse[DocumentResponse], status_code=201)
def register_document(
    payload: DocumentCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("documents:create")),
    db: Session = Depends(get_db),
):
    document = service.register_document(db, ctx.user.org_id, payload, ctx.user.id)
    return APIResponse(data=_serialize_document(document))


@router.get("", response_model=APIResponse[DocumentListResponse])
def list_documents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ctx: CurrentUserContext = Depends(require_permission("documents:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_documents(db, ctx.user.org_id, page, page_size)
    return APIResponse(
        data=DocumentListResponse(
            items=[_serialize_document(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.get("/{document_id}", response_model=APIResponse[DocumentResponse])
def get_document(
    document_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("documents:read")),
    db: Session = Depends(get_db),
):
    document = service.get_document(db, ctx.user.org_id, document_id)
    return APIResponse(data=_serialize_document(document))


@router.get("/{document_id}/download-url", response_model=APIResponse[DocumentDownloadResponse])
def get_download_url(
    document_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("documents:read")),
    db: Session = Depends(get_db),
    s3: S3Service = Depends(get_s3_service),
):
    url = service.get_download_url(db, ctx.user.org_id, document_id, s3)
    return APIResponse(data=DocumentDownloadResponse(download_url=url))


@router.post("/{document_id}/link", response_model=APIResponse[MessageResponse])
def link_document(
    document_id: UUID,
    payload: DocumentLinkRequest,
    ctx: CurrentUserContext = Depends(require_permission("documents:create")),
    db: Session = Depends(get_db),
):
    service.link_document(db, ctx.user.org_id, document_id, payload, ctx.user.id)
    return APIResponse(data=MessageResponse(message="Document linked successfully"))
