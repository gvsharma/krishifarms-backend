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

export interface ProcurementDeduction {
  id: string;
  deduction_type: string;
  deduction_type_te: string | null;
  amount: string;
  notes: string | null;
}

export interface ProcurementListItem {
  id: string;
  procurement_number: string;
  farmer_id: string;
  farmer_name: string | null;
  crop_type_id: string;
  crop_type_name: string | null;
  village_id: string;
  buyer_id?: string | null;
  buyer_name?: string | null;
  payment_terms?: string | null;
  expected_payment_date?: string | null;
  procurement_date: string;
  net_weight_kg: string;
  net_amount: string;
  status: ProcurementStatus;
  tags: string[];
}

export interface ProcurementDetail extends ProcurementListItem {
  org_id: string;
  village_name: string | null;
  payment_terms_custom?: string | null;
  actual_payment_date?: string | null;
  bag_count: number;
  gross_weight_kg: string;
  moisture_pct: string | null;
  rate_per_quintal: string;
  gross_amount: string;
  deduction_amount: string;
  notes: string | null;
  confirmed_at: string | null;
  confirmed_by_name: string | null;
  cancelled_at: string | null;
  cancellation_reason: string | null;
  deductions: ProcurementDeduction[];
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

function dateQuery(procurementDate: string): string {
  return new URLSearchParams({ procurement_date: procurementDate }).toString();
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
  return fetchApi<ProcurementDetail>(`/procurements/${id}?${dateQuery(procurementDate)}`, {
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
  buyer_id?: string | null;
  payment_terms?: string | null;
  payment_terms_custom?: string | null;
  expected_payment_date?: string | null;
  notes?: string | null;
}): Promise<ProcurementDetail> {
  return fetchApi<ProcurementDetail>("/procurements", {
    method: "POST",
    body: payload,
    clientHeaders: true,
  });
}

export function updateProcurement(
  id: string,
  procurementDate: string,
  payload: {
    farmer_id?: string;
    crop_type_id?: string;
    village_id?: string;
    bag_count?: number;
    buyer_id?: string | null;
    payment_terms?: string | null;
    payment_terms_custom?: string | null;
    expected_payment_date?: string | null;
    notes?: string | null;
  },
): Promise<ProcurementDetail> {
  return fetchApi<ProcurementDetail>(`/procurements/${id}?${dateQuery(procurementDate)}`, {
    method: "PATCH",
    body: payload,
    clientHeaders: true,
  });
}

export function submitProcurement(id: string, procurementDate: string): Promise<ProcurementDetail> {
  return fetchApi<ProcurementDetail>(`/procurements/${id}/submit?${dateQuery(procurementDate)}`, {
    method: "POST",
    clientHeaders: true,
  });
}

export function recordWeighment(
  id: string,
  procurementDate: string,
  payload: {
    gross_weight_kg: string;
    tare_weight_kg?: string;
    moisture_pct?: string | null;
    bag_count?: number | null;
  },
): Promise<ProcurementDetail> {
  return fetchApi<ProcurementDetail>(
    `/procurements/${id}/weighment?${dateQuery(procurementDate)}`,
    {
      method: "POST",
      body: payload,
      clientHeaders: true,
    },
  );
}

export function applyPrice(id: string, procurementDate: string): Promise<ProcurementDetail> {
  return fetchApi<ProcurementDetail>(
    `/procurements/${id}/apply-price?${dateQuery(procurementDate)}`,
    {
      method: "POST",
      clientHeaders: true,
    },
  );
}

export function confirmProcurement(
  id: string,
  procurementDate: string,
): Promise<ProcurementDetail> {
  return fetchApi<ProcurementDetail>(`/procurements/${id}/confirm?${dateQuery(procurementDate)}`, {
    method: "POST",
    clientHeaders: true,
  });
}

export function cancelProcurement(
  id: string,
  procurementDate: string,
  reason: string,
): Promise<ProcurementDetail> {
  return fetchApi<ProcurementDetail>(`/procurements/${id}/cancel?${dateQuery(procurementDate)}`, {
    method: "POST",
    body: { reason },
    clientHeaders: true,
  });
}

export function reverseProcurement(
  id: string,
  procurementDate: string,
  reason: string,
): Promise<ProcurementDetail> {
  return fetchApi<ProcurementDetail>(`/procurements/${id}/reverse?${dateQuery(procurementDate)}`, {
    method: "POST",
    body: { reason },
    clientHeaders: true,
  });
}

export function addProcurementDeduction(
  id: string,
  procurementDate: string,
  payload: {
    deduction_type: string;
    deduction_type_te?: string | null;
    amount: string;
    notes?: string | null;
  },
): Promise<ProcurementDetail> {
  return fetchApi<ProcurementDetail>(
    `/procurements/${id}/deductions?${dateQuery(procurementDate)}`,
    {
      method: "POST",
      body: payload,
      clientHeaders: true,
    },
  );
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

/** MUI Chip color mapping for color-coded status. */
export const STATUS_COLORS: Record<
  ProcurementStatus,
  "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning"
> = {
  draft: "default",
  pending_weighment: "warning",
  weighed: "info",
  priced: "secondary",
  confirmed: "success",
  paid_partial: "success",
  paid_full: "success",
  cancelled: "error",
  reversed: "error",
};

export const CANCELLABLE_STATUSES: ProcurementStatus[] = [
  "draft",
  "pending_weighment",
  "weighed",
];
