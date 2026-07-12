import { fetchApi } from "@/lib/api/client";

export interface FieldServiceRecord {
  id: string;
  record_number: string;
  service_category: string;
  activity_type_name?: string | null;
  farmer_name?: string | null;
  farmer_phone?: string | null;
  service_date: string;
  total_amount: string;
  pending_amount: string;
  status: string;
  comments?: string | null;
}

export interface FieldServiceListResponse {
  items: FieldServiceRecord[];
  total: number;
  page: number;
  page_size: number;
}

export async function fetchFieldServices(params?: {
  service_category?: string;
  page?: number;
  page_size?: number;
}) {
  const search = new URLSearchParams();
  if (params?.service_category) search.set("service_category", params.service_category);
  if (params?.page) search.set("page", String(params.page));
  if (params?.page_size) search.set("page_size", String(params.page_size));
  const qs = search.toString();
  return fetchApi<FieldServiceListResponse>(`/field-services${qs ? `?${qs}` : ""}`);
}
