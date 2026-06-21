from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.modules.documents.models import Document, DocumentLink
from app.modules.documents.schemas import DocumentCreateRequest, DocumentLinkRequest, PresignUploadRequest
from app.shared.services.audit import write_audit_log
from app.shared.services.s3 import S3Service


def presign_upload(db: Session, org_id: UUID, payload: PresignUploadRequest, s3: S3Service) -> dict[str, str]:
    object_key = s3.build_object_key(str(org_id), payload.document_type, payload.file_name)
    return s3.generate_presigned_upload_url(object_key=object_key, content_type=payload.mime_type)


def register_document(
    db: Session,
    org_id: UUID,
    payload: DocumentCreateRequest,
    actor_user_id: UUID,
) -> Document:
    document = Document(
        org_id=org_id,
        document_type=payload.document_type,
        file_name=payload.file_name,
        mime_type=payload.mime_type,
        file_size_bytes=payload.file_size_bytes,
        s3_bucket=settings.s3_bucket_name,
        s3_key=payload.object_key,
        checksum_sha256=payload.checksum_sha256,
        metadata_=payload.metadata,
        uploaded_by=actor_user_id,
        created_by=actor_user_id,
        updated_by=actor_user_id,
    )
    db.add(document)
    db.flush()
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="document",
        entity_id=document.id,
        after_state={"file_name": document.file_name, "document_type": document.document_type},
    )
    db.commit()
    db.refresh(document)
    return document


def get_document(db: Session, org_id: UUID, document_id: UUID) -> Document:
    document = db.query(Document).filter(Document.id == document_id, Document.org_id == org_id).first()
    if document is None:
        raise NotFoundError("Document not found")
    return document


def list_documents(db: Session, org_id: UUID, page: int, page_size: int) -> tuple[list[Document], int]:
    query = db.query(Document).filter(Document.org_id == org_id).order_by(Document.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def link_document(
    db: Session,
    org_id: UUID,
    document_id: UUID,
    payload: DocumentLinkRequest,
    actor_user_id: UUID,
) -> DocumentLink:
    document = get_document(db, org_id, document_id)
    link = DocumentLink(
        document_id=document.id,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        link_role=payload.link_role,
    )
    db.add(link)
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="LINK",
        entity_type="document",
        entity_id=document.id,
        after_state=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(link)
    return link


def get_download_url(db: Session, org_id: UUID, document_id: UUID, s3: S3Service) -> str:
    document = get_document(db, org_id, document_id)
    return s3.generate_presigned_download_url(object_key=document.s3_key)
