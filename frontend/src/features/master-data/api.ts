import { fetchApi } from "@/lib/api/client";

export interface Village {
  id: string;
  name: string;
  name_te: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface VillageListData {
  items: Village[];
  total: number;
  page: number;
  page_size: number;
}

export function fetchVillages(page = 1, pageSize = 50): Promise<VillageListData> {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return fetchApi<VillageListData>(`/villages?${params}`, { method: "GET", clientHeaders: false });
}

export function createVillage(payload: {
  name: string;
  name_te?: string | null;
}): Promise<Village> {
  return fetchApi<Village>("/villages", {
    method: "POST",
    body: payload,
    clientHeaders: true,
  });
}
