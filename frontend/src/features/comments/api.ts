import { fetchApi } from "@/lib/api/client";

export interface Comment {
  id: string;
  entity_type: string;
  entity_id: string;
  body: string;
  body_te: string | null;
  author_user_id: string;
  author_name: string | null;
  device_id: string | null;
  client_type: string | null;
  created_at: string;
}

export interface CommentListData {
  items: Comment[];
  total: number;
  page: number;
  page_size: number;
}

export interface CreateCommentPayload {
  entity_type: string;
  entity_id: string;
  body: string;
  body_te?: string | null;
}

export function fetchComments(
  entityType: string,
  entityId: string,
  page = 1,
  pageSize = 50,
): Promise<CommentListData> {
  const params = new URLSearchParams({
    entity_type: entityType,
    entity_id: entityId,
    page: String(page),
    page_size: String(pageSize),
  });
  return fetchApi<CommentListData>(`/comments?${params}`, {
    method: "GET",
    clientHeaders: false,
  });
}

export function createComment(payload: CreateCommentPayload): Promise<Comment> {
  return fetchApi<Comment>("/comments", {
    method: "POST",
    body: payload,
    clientHeaders: true,
  });
}
