"use client";

import {
  Alert,
  Avatar,
  Box,
  Button,
  CircularProgress,
  Divider,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { Send } from "@mui/icons-material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import {
  createComment,
  fetchComments,
  type Comment,
} from "@/features/comments/api";

export interface CommentThreadProps {
  entityType: string;
  entityId: string;
  title?: string;
}

function formatRelativeTime(iso: string): string {
  const date = new Date(iso);
  const diffMs = Date.now() - date.getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return date.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

function CommentItem({ comment }: { comment: Comment }) {
  const initials = (comment.author_name ?? "?")
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <Stack direction="row" spacing={1.5} alignItems="flex-start">
      <Avatar sx={{ width: 32, height: 32, fontSize: 12, bgcolor: "primary.main" }}>
        {initials}
      </Avatar>
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <Stack direction="row" spacing={1} alignItems="baseline">
          <Typography variant="subtitle2">{comment.author_name ?? "Unknown"}</Typography>
          <Typography variant="caption" color="text.secondary">
            {formatRelativeTime(comment.created_at)}
          </Typography>
          {comment.client_type && (
            <Typography variant="caption" color="text.secondary">
              · {comment.client_type}
            </Typography>
          )}
        </Stack>
        <Typography variant="body2" sx={{ mt: 0.5, whiteSpace: "pre-wrap" }}>
          {comment.body}
        </Typography>
        {comment.body_te && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            {comment.body_te}
          </Typography>
        )}
      </Box>
    </Stack>
  );
}

export function CommentThread({ entityType, entityId, title = "Comments" }: CommentThreadProps) {
  const [body, setBody] = useState("");
  const queryClient = useQueryClient();
  const queryKey = ["comments", entityType, entityId];

  const { data, isLoading, isError, error } = useQuery({
    queryKey,
    queryFn: () => fetchComments(entityType, entityId),
    enabled: Boolean(entityType && entityId),
  });

  const mutation = useMutation({
    mutationFn: (text: string) =>
      createComment({ entity_type: entityType, entity_id: entityId, body: text }),
    onSuccess: () => {
      setBody("");
      queryClient.invalidateQueries({ queryKey });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = body.trim();
    if (!trimmed || mutation.isPending) return;
    mutation.mutate(trimmed);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>

      {isLoading && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 3 }}>
          <CircularProgress size={28} />
        </Box>
      )}

      {isError && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {error instanceof Error ? error.message : "Could not load comments"}
        </Alert>
      )}

      {!isLoading && data && data.items.length === 0 && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          No comments yet. Add the first note below.
        </Typography>
      )}

      <Stack spacing={2} sx={{ mb: 2 }}>
        {data?.items.map((comment) => (
          <CommentItem key={comment.id} comment={comment} />
        ))}
      </Stack>

      <Divider sx={{ mb: 2 }} />

      <Box component="form" onSubmit={handleSubmit}>
        <TextField
          fullWidth
          multiline
          minRows={2}
          placeholder="Add a comment…"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          disabled={mutation.isPending}
          size="small"
        />
        {mutation.isError && (
          <Alert severity="error" sx={{ mt: 1 }}>
            {mutation.error instanceof Error ? mutation.error.message : "Failed to post comment"}
          </Alert>
        )}
        <Stack direction="row" justifyContent="flex-end" sx={{ mt: 1 }}>
          <Button
            type="submit"
            variant="contained"
            size="small"
            startIcon={<Send />}
            disabled={!body.trim() || mutation.isPending}
          >
            {mutation.isPending ? "Posting…" : "Post comment"}
          </Button>
        </Stack>
      </Box>
    </Box>
  );
}
