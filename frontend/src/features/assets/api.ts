import { fetchApi } from "@/lib/api/client";

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface Asset {
  id: string;
  org_id: string;
  asset_code: string;
  name: string;
  name_te: string | null;
  asset_category: string;
  vehicle_type_id: string | null;
  vehicle_type_name: string | null;
  vehicle_type_code: string | null;
  registration_number: string | null;
  fuel_type: string | null;
  driver_name: string | null;
  status: string;
  is_rentable: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface AssetCreatePayload {
  name: string;
  asset_code?: string | null;
  asset_category: string;
  vehicle_type_id?: string | null;
  registration_number?: string | null;
  fuel_type?: string | null;
  driver_name?: string | null;
  status?: string;
  notes?: string | null;
}

function pageParams(page = 1, pageSize = 50): string {
  return new URLSearchParams({ page: String(page), page_size: String(pageSize) }).toString();
}

export function fetchAssets(page = 1, pageSize = 50): Promise<Paginated<Asset>> {
  return fetchApi(`/assets?${pageParams(page, pageSize)}`);
}

export function createAsset(payload: AssetCreatePayload): Promise<Asset> {
  return fetchApi("/assets", { method: "POST", body: payload, clientHeaders: true });
}

export function updateAsset(id: string, payload: Partial<AssetCreatePayload>): Promise<Asset> {
  return fetchApi(`/assets/${id}`, { method: "PATCH", body: payload, clientHeaders: true });
}

export function deleteAsset(id: string): Promise<{ message: string }> {
  return fetchApi(`/assets/${id}`, { method: "DELETE", clientHeaders: true });
}
