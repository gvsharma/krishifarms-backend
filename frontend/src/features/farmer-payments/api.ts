import { fetchApi } from "@/lib/api/client";

export type FarmerPaymentType = "advance" | "final" | "adjustment";
export type FarmerPaymentStatus = "pending" | "completed" | "failed" | "reversed";

export interface FarmerPaymentAllocation {
  id: string;
  procurement_id: string | null;
  procurement_date: string | null;
  allocated_amount: string;
}

export interface FarmerPayment {
  id: string;
  payment_number: string;
  farmer_id: string;
  payment_type: FarmerPaymentType | string;
  payment_date: string;
  amount: string;
  payment_mode_id: string;
  reference_no: string | null;
  bank_account_id: string | null;
  status: FarmerPaymentStatus | string;
  notes: string | null;
  allocations: FarmerPaymentAllocation[];
}

export interface FarmerPaymentListResponse {
  items: FarmerPayment[];
  total: number;
  page: number;
  page_size: number;
}

export interface CreateFarmerPaymentPayload {
  farmer_id: string;
  payment_type: FarmerPaymentType;
  payment_date: string;
  amount: string;
  payment_mode_id: string;
  bank_account_id?: string | null;
  reference_no?: string | null;
  notes?: string | null;
}

export const PAYMENT_TYPE_LABELS: Record<string, string> = {
  advance: "Advance",
  final: "Final",
  adjustment: "Adjustment",
};

export async function fetchFarmerPayments(params?: {
  page?: number;
  pageSize?: number;
  farmer_id?: string;
  payment_type?: FarmerPaymentType;
  date_from?: string;
  date_to?: string;
}): Promise<FarmerPaymentListResponse> {
  const search = new URLSearchParams();
  if (params?.page) search.set("page", String(params.page));
  if (params?.pageSize) search.set("page_size", String(params.pageSize));
  if (params?.farmer_id) search.set("farmer_id", params.farmer_id);
  if (params?.payment_type) search.set("payment_type", params.payment_type);
  if (params?.date_from) search.set("date_from", params.date_from);
  if (params?.date_to) search.set("date_to", params.date_to);
  const qs = search.toString();
  return fetchApi<FarmerPaymentListResponse>(`/farmer-payments${qs ? `?${qs}` : ""}`);
}

export function createFarmerPayment(
  payload: CreateFarmerPaymentPayload,
): Promise<FarmerPayment> {
  return fetchApi<FarmerPayment>("/farmer-payments", {
    method: "POST",
    body: payload,
    clientHeaders: true,
  });
}

export function fetchFarmerPayment(
  id: string,
  paymentDate: string,
): Promise<FarmerPayment> {
  return fetchApi<FarmerPayment>(
    `/farmer-payments/${id}?payment_date=${encodeURIComponent(paymentDate)}`,
  );
}

export interface AllocatePaymentItem {
  procurement_id: string;
  procurement_date: string;
  allocated_amount: string;
}

export interface AllocateFarmerPaymentPayload {
  allocations: AllocatePaymentItem[];
}

export function allocateFarmerPayment(
  id: string,
  paymentDate: string,
  payload: AllocateFarmerPaymentPayload,
): Promise<FarmerPayment> {
  return fetchApi<FarmerPayment>(
    `/farmer-payments/${id}/allocate?payment_date=${encodeURIComponent(paymentDate)}`,
    {
      method: "POST",
      body: payload,
      clientHeaders: true,
    },
  );
}

export function reverseFarmerPayment(
  id: string,
  paymentDate: string,
  reason: string,
): Promise<FarmerPayment> {
  return fetchApi<FarmerPayment>(
    `/farmer-payments/${id}/reverse?payment_date=${encodeURIComponent(paymentDate)}`,
    {
      method: "POST",
      body: { reason },
      clientHeaders: true,
    },
  );
}

export const PAYMENT_STATUS_LABELS: Record<string, string> = {
  pending: "Pending",
  completed: "Completed",
  failed: "Failed",
  reversed: "Reversed",
};

export const PAYMENT_STATUS_COLORS: Record<
  string,
  "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning"
> = {
  pending: "warning",
  completed: "success",
  failed: "error",
  reversed: "error",
};

/** Sum allocated amounts on a payment (string Decimal values). */
export function allocatedTotal(payment: FarmerPayment): number {
  return payment.allocations.reduce((sum, a) => sum + Number(a.allocated_amount || 0), 0);
}

export function unallocatedRemainder(payment: FarmerPayment): number {
  const rem = Number(payment.amount) - allocatedTotal(payment);
  return Number.isFinite(rem) ? Math.max(0, Math.round(rem * 100) / 100) : 0;
}
