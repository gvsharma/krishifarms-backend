import { fetchApi } from "@/lib/api/client";
import type { ServiceCategory } from "./constants";

export interface FieldServiceRecord {
  id: string;
  record_number: string;
  service_category: ServiceCategory;
  activity_type_id: string | null;
  activity_type_name?: string | null;
  farmer_id: string | null;
  farmer_name?: string | null;
  farmer_phone?: string | null;
  asset_id: string | null;
  vehicle_type_id: string | null;
  vehicle_type_name?: string | null;
  service_date: string;
  location: string | null;
  location_te: string | null;
  hours: string | null;
  bag_count: number | null;
  quantity: string | null;
  quantity_unit: string | null;
  rate_per_unit: string | null;
  diesel_amount: string;
  diesel_expense_id?: string | null;
  amount_given: string;
  advance_amount: string;
  total_amount: string;
  pending_amount: string;
  cleaning_status: string | null;
  facility_status: string | null;
  status: string;
  comments: string | null;
  comments_te: string | null;
  created_at: string;
  updated_at: string;
}

export interface FieldServiceListResponse {
  items: FieldServiceRecord[];
  total: number;
  page: number;
  page_size: number;
}

export interface FieldServiceCreatePayload {
  service_category: ServiceCategory;
  service_date: string;
  activity_type_id?: string | null;
  farmer_id?: string | null;
  asset_id?: string | null;
  vehicle_type_id?: string | null;
  location?: string | null;
  location_te?: string | null;
  hours?: string | null;
  bag_count?: number | null;
  quantity?: string | null;
  quantity_unit?: string | null;
  rate_per_unit?: string | null;
  diesel_amount?: string;
  amount_given?: string;
  advance_amount?: string;
  total_amount?: string;
  pending_amount?: string;
  cleaning_status?: string | null;
  facility_status?: string | null;
  status?: string;
  comments?: string | null;
  comments_te?: string | null;
}

export type FieldServiceUpdatePayload = Omit<FieldServiceCreatePayload, "service_category">;

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

export function fetchFieldService(id: string): Promise<FieldServiceRecord> {
  return fetchApi<FieldServiceRecord>(`/field-services/${id}`);
}

export function createFieldService(payload: FieldServiceCreatePayload): Promise<FieldServiceRecord> {
  return fetchApi<FieldServiceRecord>("/field-services", {
    method: "POST",
    body: payload,
    clientHeaders: true,
  });
}

export function updateFieldService(
  id: string,
  payload: FieldServiceUpdatePayload,
): Promise<FieldServiceRecord> {
  return fetchApi<FieldServiceRecord>(`/field-services/${id}`, {
    method: "PATCH",
    body: payload,
    clientHeaders: true,
  });
}

export function deleteFieldService(id: string): Promise<{ message: string }> {
  return fetchApi<{ message: string }>(`/field-services/${id}`, {
    method: "DELETE",
    clientHeaders: true,
  });
}
