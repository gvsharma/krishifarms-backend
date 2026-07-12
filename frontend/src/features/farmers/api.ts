import { fetchApi } from "@/lib/api/client";

export interface FarmerListItem {
  id: string;
  farmer_code: string;
  full_name: string;
  full_name_te: string | null;
  phone_primary: string;
  village_id: string;
  village_name: string | null;
  status: string;
  tags: string[];
}

export interface FarmerDetail extends FarmerListItem {
  org_id: string;
  father_name: string | null;
  father_name_te: string | null;
  phone_secondary: string | null;
  address: string | null;
  address_te: string | null;
  aadhaar_last4: string | null;
  notes: string | null;
  outstanding_amount: string | null;
  tags: string[];
  bank_accounts: BankAccount[];
  land_parcels: LandParcel[];
  comments: { id: string; body: string; author_name: string | null; created_at: string }[];
}

export interface BankAccount {
  id: string;
  account_holder_name: string;
  bank_name: string;
  branch: string | null;
  ifsc: string;
  account_number_masked: string;
  is_primary: boolean;
}

export interface LandParcel {
  id: string;
  survey_number: string;
  acres: string;
  land_type: string | null;
  location_notes: string | null;
  geo_lat: string | null;
  geo_lng: string | null;
}

export interface FarmerListData {
  items: FarmerListItem[];
  total: number;
  page: number;
  page_size: number;
}

export function fetchFarmers(params?: {
  page?: number;
  pageSize?: number;
  q?: string;
  villageId?: string;
}): Promise<FarmerListData> {
  const search = new URLSearchParams({
    page: String(params?.page ?? 1),
    page_size: String(params?.pageSize ?? 20),
  });
  if (params?.q) search.set("q", params.q);
  if (params?.villageId) search.set("village_id", params.villageId);
  return fetchApi<FarmerListData>(`/farmers?${search}`, { method: "GET", clientHeaders: false });
}

export function fetchFarmer(id: string): Promise<FarmerDetail> {
  return fetchApi<FarmerDetail>(`/farmers/${id}`, { method: "GET", clientHeaders: false });
}

export function createFarmer(payload: {
  full_name: string;
  phone_primary: string;
  village_id: string;
  full_name_te?: string | null;
  notes?: string | null;
}): Promise<FarmerDetail> {
  return fetchApi<FarmerDetail>("/farmers", {
    method: "POST",
    body: payload,
    clientHeaders: true,
  });
}

export function updateFarmer(
  id: string,
  payload: Partial<{
    full_name: string;
    full_name_te: string | null;
    phone_primary: string;
    phone_secondary: string | null;
    village_id: string;
    address: string | null;
    notes: string | null;
    status: string;
  }>,
): Promise<FarmerDetail> {
  return fetchApi<FarmerDetail>(`/farmers/${id}`, {
    method: "PATCH",
    body: payload,
    clientHeaders: true,
  });
}
