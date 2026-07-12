import { fetchApi } from "@/lib/api/client";

export interface DocumentItem {
  id: string;
  org_id: string;
  document_type: string;
  file_name: string;
  mime_type: string;
  file_size_bytes: number;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface PresignUploadResult {
  upload_url: string;
  object_key: string;
  bucket: string;
}

export function presignDocumentUpload(payload: {
  document_type: string;
  file_name: string;
  mime_type: string;
  file_size_bytes: number;
}): Promise<PresignUploadResult> {
  return fetchApi<PresignUploadResult>("/documents/presign-upload", {
    method: "POST",
    body: payload,
    clientHeaders: true,
  });
}

export function registerDocument(payload: {
  document_type: string;
  file_name: string;
  mime_type: string;
  file_size_bytes: number;
  object_key: string;
  metadata?: Record<string, unknown>;
}): Promise<DocumentItem> {
  return fetchApi<DocumentItem>("/documents", {
    method: "POST",
    body: payload,
    clientHeaders: true,
  });
}

export function linkDocument(
  documentId: string,
  payload: { entity_type: string; entity_id: string; link_role?: string },
): Promise<{ message: string }> {
  return fetchApi<{ message: string }>(`/documents/${documentId}/link`, {
    method: "POST",
    body: payload,
    clientHeaders: true,
  });
}

export function getDocumentDownloadUrl(documentId: string): Promise<{ download_url: string }> {
  return fetchApi<{ download_url: string }>(`/documents/${documentId}/download-url`, {
    method: "GET",
    clientHeaders: false,
  });
}

export interface DocumentListResponse {
  items: DocumentItem[];
  total: number;
  page: number;
  page_size: number;
}

/** List documents linked to an entity (`entity_type` + `entity_id` required together). */
export function fetchDocumentsForEntity(params: {
  entityType: string;
  entityId: string;
  page?: number;
  pageSize?: number;
}): Promise<DocumentListResponse> {
  const search = new URLSearchParams({
    entity_type: params.entityType,
    entity_id: params.entityId,
    page: String(params.page ?? 1),
    page_size: String(params.pageSize ?? 50),
  });
  return fetchApi<DocumentListResponse>(`/documents?${search}`, {
    method: "GET",
    clientHeaders: false,
  });
}

/**
 * Presign → PUT to S3 → register → link to entity.
 */
export async function uploadAndLinkDocument(opts: {
  file: File;
  documentType?: string;
  entityType: string;
  entityId: string;
  linkRole?: string;
}): Promise<DocumentItem> {
  const documentType = opts.documentType ?? "photo";
  const presign = await presignDocumentUpload({
    document_type: documentType,
    file_name: opts.file.name,
    mime_type: opts.file.type || "application/octet-stream",
    file_size_bytes: opts.file.size,
  });

  const put = await fetch(presign.upload_url, {
    method: "PUT",
    body: opts.file,
    headers: {
      "Content-Type": opts.file.type || "application/octet-stream",
    },
  });
  if (!put.ok) {
    throw new Error(`Upload to storage failed (${put.status})`);
  }

  const doc = await registerDocument({
    document_type: documentType,
    file_name: opts.file.name,
    mime_type: opts.file.type || "application/octet-stream",
    file_size_bytes: opts.file.size,
    object_key: presign.object_key,
    metadata: {
      entity_type: opts.entityType,
      entity_id: opts.entityId,
    },
  });

  await linkDocument(doc.id, {
    entity_type: opts.entityType,
    entity_id: opts.entityId,
    link_role: opts.linkRole ?? "primary_attachment",
  });

  return doc;
}
