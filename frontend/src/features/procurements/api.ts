import { fetchApi } from "@/lib/api/client";

export type ProcurementStatus =
  | "draft"
  | "pending_weighment"
  | "weighed"
  | "priced"
  | "confirmed"
  | "paid_partial"
  | "paid_full"
  | "cancelled"
  | "reversed";

export interface ProcurementListItem {
  id: string;
  procurement_number: string;
  farmer_id: string;
  farmer_name: string | null;
  crop_type_id: string;
  crop_type_name: string | null;
  village_id: string;
  procurement_date: string;
  net_weight_kg: string;
  net_amount: string;
  status: ProcurementStatus;
  tags: string[];
}

export interface ProcurementDetail extends ProcurementListItem {
  org_id: string;
  village_name: string | null;
  bag_count: number;
  gross_weight_kg: string;
  moisture_pct: string | null;
  rate_per_quintal: string;
  gross_amount: string;
  deduction_amount: string;
  notes: string | null;
  comments: { id: string; body: string; author_name: string | null; created_at: string }[];
}

export interface ProcurementListData {
  items: ProcurementListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface CropType {
  id: string;
  name: string;
  code: string;
  is_active: boolean;
}

export interface CropTypeListData {
  items: CropType[];
  total: number;
  page: number;
  page_size: number;
}

export function fetchProcurements(params?: {
  page?: number;
  pageSize?: number;
  status?: ProcurementStatus;
}): Promise<ProcurementListData> {
  const search = new URLSearchParams({
    page: String(params?.page ?? 1),
    page_size: String(params?.pageSize ?? 20),
  });
  if (params?.status) search.set("status", params.status);
  return fetchApi<ProcurementListData>(`/procurements?${search}`, {
    method: "GET",
    clientHeaders: false,
  });
}

export function fetchProcurement(id: string, procurementDate: string): Promise<ProcurementDetail> {
  const search = new URLSearchParams({ procurement_date: procurementDate });
  return fetchApi<ProcurementDetail>(`/procurements/${id}?${search}`, {
    method: "GET",
    clientHeaders: false,
  });
}

export function createProcurement(payload: {
  farmer_id: string;
  crop_type_id: string;
  village_id: string;
  procurement_date: string;
  bag_count?: number;
  notes?: string | null;
}): Promise<ProcurementDetail> {
  return fetchApi<ProcurementDetail>("/procurements", {
    method: "POST",
    body: payload,
    clientHeaders: true,
  });
}

export function fetchCropTypes(): Promise<CropTypeListData> {
  return fetchApi<CropTypeListData>("/crop-types?page=1&page_size=50", {
    method: "GET",
    clientHeaders: false,
  });
}

export function formatInr(value: string | number): string {
  const num = typeof value === "string" ? Number(value) : value;
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(Number.isFinite(num) ? num : 0);
}

export const STATUS_LABELS: Record<ProcurementStatus, string> = {
  draft: "Draft",
  pending_weighment: "Pending weighment",
  weighed: "Weighed",
  priced: "Priced",
  confirmed: "Confirmed",
  paid_partial: "Partially paid",
  paid_full: "Paid in full",
  cancelled: "Cancelled",
  reversed: "Reversed",
};
