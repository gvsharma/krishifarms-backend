import { fetchApi } from "@/lib/fetch-api";

export interface HamaliDailyLine {
  farmer_id: string;
  farmer_name: string;
  bag_count: number;
  tip_amount: string;
}

export interface HamaliDaily {
  work_date: string;
  total_bags: number;
  total_tips: string;
  lines: HamaliDailyLine[];
}

export interface HamaliSummary {
  period: string;
  date_from: string;
  date_to: string;
  total_bags: number;
  total_tips: string;
  days_worked: number;
  by_farmer: HamaliDailyLine[];
  by_day: HamaliDaily[];
}

export interface HamaliWorkEntry {
  id: string;
  worker_id: string;
  farmer_id: string;
  work_date: string;
  bag_count: number;
  tip_amount: string;
  farmer_name?: string | null;
  worker_name?: string | null;
  notes?: string | null;
}

export interface HamaliWorker {
  id: string;
  worker_code: string;
  full_name: string;
  phone?: string | null;
  status: string;
}

export async function fetchHamaliDaily(workDate: string): Promise<HamaliDaily> {
  const res = await fetchApi<{ data: HamaliDaily }>(
    `/hamali/me/daily?work_date=${encodeURIComponent(workDate)}`,
  );
  return res.data;
}

export async function fetchHamaliSummary(
  period: "week" | "month",
  anchorDate: string,
): Promise<HamaliSummary> {
  const res = await fetchApi<{ data: HamaliSummary }>(
    `/hamali/me/summary?period=${period}&anchor_date=${encodeURIComponent(anchorDate)}`,
  );
  return res.data;
}

export async function fetchHamaliWorkEntries(params?: {
  worker_id?: string;
  work_date?: string;
}): Promise<HamaliWorkEntry[]> {
  const q = new URLSearchParams({ page: "1", page_size: "100" });
  if (params?.worker_id) q.set("worker_id", params.worker_id);
  if (params?.work_date) q.set("work_date", params.work_date);
  const res = await fetchApi<{ data: { items: HamaliWorkEntry[] } }>(
    `/hamali/work-entries?${q}`,
  );
  return res.data.items;
}

export async function fetchHamaliWorkers(): Promise<HamaliWorker[]> {
  const res = await fetchApi<{ data: { items: HamaliWorker[] } }>(
    "/hamali/workers?page=1&page_size=100",
  );
  return res.data.items;
}

export async function createHamaliWorkEntry(payload: {
  worker_id: string;
  farmer_id: string;
  work_date: string;
  bag_count: number;
  tip_amount: string;
  notes?: string;
}): Promise<HamaliWorkEntry> {
  const res = await fetchApi<{ data: HamaliWorkEntry }>("/hamali/work-entries", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return res.data;
}
