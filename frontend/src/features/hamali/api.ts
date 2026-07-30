import { fetchApi } from "@/lib/api/client";

export interface HamaliWorker {
  id: string;
  worker_code: string;
  full_name: string;
  full_name_te: string | null;
  phone: string | null;
  default_rate_per_bag: string;
  status: "active" | "inactive";
}

export interface HamaliDailyEntry {
  id: string;
  hamali_worker_id: string;
  worker_name: string | null;
  worker_code: string | null;
  entry_date: string;
  bags_lifted: number;
  rate_per_bag: string;
  labor_amount: string;
  maintenance_amount: string;
  tip_amount: string;
  total_amount: string;
  payment_status: "pending" | "scheduled" | "paid";
  weekly_payment_id: string | null;
  notes: string | null;
}

export interface HamaliDailySummary {
  total_bags: number;
  total_labor_amount: string;
  total_maintenance_amount: string;
  total_tip_amount: string;
  total_amount: string;
}

export interface HamaliWeeklyPayment {
  id: string;
  payment_number: string;
  week_start_date: string;
  week_end_date: string;
  total_bags: number;
  total_labor_amount: string;
  total_maintenance_amount: string;
  total_tip_amount: string;
  total_amount: string;
  status: "draft" | "paid";
  paid_at: string | null;
  paid_by_name: string | null;
  payment_reference: string | null;
  notes: string | null;
}

export interface HamaliWorkerWeekSummary {
  hamali_worker_id: string;
  worker_name: string;
  worker_code: string;
  days_worked: number;
  total_bags: number;
  total_labor_amount: string;
  total_maintenance_amount: string;
  total_tip_amount: string;
  total_amount: string;
}

export interface HamaliWeeklySummary {
  week_start_date: string;
  week_end_date: string;
  pending_entries: number;
  total_bags: number;
  total_labor_amount: string;
  total_maintenance_amount: string;
  total_tip_amount: string;
  total_amount: string;
  by_worker: HamaliWorkerWeekSummary[];
}

export function fetchHamaliWorkers(params?: {
  page?: number;
  pageSize?: number;
  status?: string;
  q?: string;
}): Promise<{ items: HamaliWorker[]; total: number; page: number; page_size: number }> {
  const search = new URLSearchParams({
    page: String(params?.page ?? 1),
    page_size: String(params?.pageSize ?? 100),
  });
  if (params?.status) search.set("status", params.status);
  if (params?.q) search.set("q", params.q);
  return fetchApi(`/hamali/workers?${search}`, { method: "GET", clientHeaders: false });
}

export function createHamaliWorker(payload: {
  full_name: string;
  full_name_te?: string | null;
  phone?: string | null;
  default_rate_per_bag?: string | null;
}): Promise<HamaliWorker> {
  return fetchApi<HamaliWorker>("/hamali/workers", {
    method: "POST",
    body: payload,
    clientHeaders: true,
  });
}

export function fetchHamaliDailyEntries(params?: {
  page?: number;
  pageSize?: number;
  date_from?: string;
  date_to?: string;
  hamali_worker_id?: string;
  payment_status?: string;
}): Promise<{
  items: HamaliDailyEntry[];
  total: number;
  page: number;
  page_size: number;
  summary: HamaliDailySummary;
}> {
  const search = new URLSearchParams({
    page: String(params?.page ?? 1),
    page_size: String(params?.pageSize ?? 50),
  });
  if (params?.date_from) search.set("date_from", params.date_from);
  if (params?.date_to) search.set("date_to", params.date_to);
  if (params?.hamali_worker_id) search.set("hamali_worker_id", params.hamali_worker_id);
  if (params?.payment_status) search.set("payment_status", params.payment_status);
  return fetchApi(`/hamali/daily-entries?${search}`, { method: "GET", clientHeaders: false });
}

export function createHamaliDailyEntry(payload: {
  hamali_worker_id: string;
  entry_date: string;
  bags_lifted: number;
  rate_per_bag?: string | null;
  maintenance_amount?: string;
  tip_amount?: string;
  notes?: string | null;
}): Promise<HamaliDailyEntry> {
  return fetchApi<HamaliDailyEntry>("/hamali/daily-entries", {
    method: "POST",
    body: payload,
    clientHeaders: true,
  });
}

export function fetchHamaliWeeklySummary(weekStartDate: string): Promise<HamaliWeeklySummary> {
  return fetchApi<HamaliWeeklySummary>(
    `/hamali/weekly-summary?week_start_date=${encodeURIComponent(weekStartDate)}`,
    { method: "GET", clientHeaders: false },
  );
}

export function fetchHamaliWeeklyPayments(params?: {
  page?: number;
  pageSize?: number;
  status?: string;
}): Promise<{ items: HamaliWeeklyPayment[]; total: number; page: number; page_size: number }> {
  const search = new URLSearchParams({
    page: String(params?.page ?? 1),
    page_size: String(params?.pageSize ?? 20),
  });
  if (params?.status) search.set("status", params.status);
  return fetchApi(`/hamali/weekly-payments?${search}`, { method: "GET", clientHeaders: false });
}

export function createHamaliWeeklyPayment(payload: {
  week_start_date: string;
  notes?: string | null;
}): Promise<HamaliWeeklyPayment> {
  return fetchApi<HamaliWeeklyPayment>("/hamali/weekly-payments", {
    method: "POST",
    body: payload,
    clientHeaders: true,
  });
}

export function markHamaliWeeklyPaymentPaid(
  paymentId: string,
  payload?: { payment_reference?: string | null; notes?: string | null },
): Promise<HamaliWeeklyPayment> {
  return fetchApi<HamaliWeeklyPayment>(`/hamali/weekly-payments/${paymentId}/mark-paid`, {
    method: "POST",
    body: payload ?? {},
    clientHeaders: true,
  });
}

/** ISO week Monday for a given YYYY-MM-DD string. */
export function mondayOf(dateStr: string): string {
  const d = new Date(`${dateStr}T12:00:00`);
  const day = d.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  d.setDate(d.getDate() + diff);
  return d.toISOString().slice(0, 10);
}

export const PAYMENT_STATUS_LABELS: Record<HamaliDailyEntry["payment_status"], string> = {
  pending: "Pending",
  scheduled: "In weekly batch",
  paid: "Paid",
};
