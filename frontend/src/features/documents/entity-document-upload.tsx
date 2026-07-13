"use client";

import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Link,
  Stack,
  Typography,
} from "@mui/material";
import { CloudUpload } from "@mui/icons-material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";
import { PermissionGuard } from "@/components/auth/permission-guard";
import {
  fetchDocumentsForEntity,
  getDocumentDownloadUrl,
  uploadAndLinkDocument,
} from "@/features/documents/api";

type UploadKind = {
  documentType: string;
  label: string;
};

type Props = {
  entityType: string;
  entityId: string;
  /** Default single upload type when `uploadKinds` is omitted. */
  documentType?: string;
  title?: string;
  /** Multiple upload buttons (e.g. fuel_bill + photo) sharing one gallery. */
  uploadKinds?: UploadKind[];
};

/**
 * Photo/document attach + entity gallery via documents list filter.
 */
export function EntityDocumentUpload({
  entityType,
  entityId,
  documentType = "photo",
  title = "Photos & documents",
  uploadKinds,
}: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const pendingTypeRef = useRef(documentType);
  const [pendingType, setPendingType] = useState(documentType);
  const queryClient = useQueryClient();
  const queryKey = ["documents", entityType, entityId];

  const kinds: UploadKind[] = uploadKinds?.length
    ? uploadKinds
    : [{ documentType, label: "Upload photo / document" }];

  const galleryQuery = useQuery({
    queryKey,
    queryFn: () => fetchDocumentsForEntity({ entityType, entityId }),
    enabled: Boolean(entityType && entityId),
  });

  const uploadMut = useMutation({
    mutationFn: (file: File) =>
      uploadAndLinkDocument({
        file,
        documentType: pendingTypeRef.current,
        entityType,
        entityId,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey });
      if (inputRef.current) inputRef.current.value = "";
    },
  });

  const openDownload = async (documentId: string) => {
    const { download_url } = await getDocumentDownloadUrl(documentId);
    window.open(download_url, "_blank", "noopener,noreferrer");
  };

  const startUpload = (kind: UploadKind) => {
    pendingTypeRef.current = kind.documentType;
    setPendingType(kind.documentType);
    inputRef.current?.click();
  };

  return (
    <Stack spacing={1.5}>
      <Typography variant="subtitle2" color="text.secondary">
        {title}
      </Typography>

      <PermissionGuard permission="documents:create">
        <input
          ref={inputRef}
          type="file"
          accept="image/*,.pdf"
          hidden
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) uploadMut.mutate(file);
          }}
        />
        <Stack direction="row" flexWrap="wrap" useFlexGap spacing={1}>
          {kinds.map((kind) => (
            <Button
              key={kind.documentType}
              variant="outlined"
              startIcon={<CloudUpload />}
              sx={{ minHeight: 48 }}
              disabled={uploadMut.isPending}
              onClick={() => startUpload(kind)}
            >
              {uploadMut.isPending && pendingType === kind.documentType
                ? "Uploading…"
                : kind.label}
            </Button>
          ))}
        </Stack>
      </PermissionGuard>

      {uploadMut.isError && (
        <Alert severity="error">
          {uploadMut.error instanceof Error ? uploadMut.error.message : "Upload failed"}
        </Alert>
      )}

      {galleryQuery.isLoading && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 2 }}>
          <CircularProgress size={22} />
        </Box>
      )}

      {galleryQuery.isError && (
        <Alert severity="warning">
          {galleryQuery.error instanceof Error
            ? galleryQuery.error.message
            : "Could not load document gallery"}
        </Alert>
      )}

      {galleryQuery.data && (
        <Stack spacing={0.5}>
          {galleryQuery.data.items.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              No linked documents yet
            </Typography>
          ) : (
            galleryQuery.data.items.map((doc) => (
              <Typography key={doc.id} variant="body2">
                <Link
                  component="button"
                  type="button"
                  variant="body2"
                  onClick={() => openDownload(doc.id)}
                  underline="hover"
                >
                  {doc.file_name}
                </Link>{" "}
                <Typography component="span" variant="caption" color="text.secondary">
                  · {doc.document_type} · {doc.created_at.slice(0, 10)}
                </Typography>
              </Typography>
            ))
          )}
        </Stack>
      )}
    </Stack>
  );
}
