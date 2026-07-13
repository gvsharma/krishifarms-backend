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
  is_vip?: boolean;
  trust_rating?: number | null;
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
  preferred_language?: string | null;
  preferred_payment_cycle?: string | null;
  preferred_payment_method?: string | null;
  trust_rating?: number | null;
  is_vip?: boolean;
  geo_lat?: string | null;
  geo_lng?: string | null;
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
  ownership?: string | null;
  irrigation_type?: string | null;
  water_source?: string | null;
  soil_type?: string | null;
  village_name?: string | null;
}

export interface FarmerListData {
  items: FarmerListItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface Farmer360Profile {
  summary: {
    id: string;
    farmer_code: string;
    full_name: string;
    full_name_te: string | null;
    phone_primary: string;
    phone_secondary: string | null;
    village_id: string;
    village_name: string | null;
    mandal: string | null;
    district: string | null;
    address: string | null;
    geo_lat: string | null;
    geo_lng: string | null;
    preferred_language: string | null;
    preferred_payment_cycle: string | null;
    preferred_payment_method: string | null;
    trust_rating: number | null;
    status: string;
    is_vip: boolean;
    status_label: string;
    tags: string[];
  };
  statistics: {
    total_services_availed: number;
    total_farming_area: string;
    total_crops_sold: number;
    total_procurement_quantity_kg: string;
    lifetime_business_value: string;
    outstanding_amount: string;
    amount_paid: string;
    current_season_procurement_kg: string;
    last_service_date: string | null;
    last_payment_date: string | null;
    pending_payments: string;
    current_crop: string | null;
    preferred_vehicle: string | null;
    preferred_payment_method: string | null;
  };
  timeline: {
    event_type: string;
    title: string;
    description: string | null;
    occurred_at: string;
    entity_type: string | null;
    entity_id: string | null;
    amount: string | null;
  }[];
  services: Record<string, unknown>[];
  farming: Record<string, unknown>[];
  procurements: Record<string, unknown>[];
  finance: Record<string, unknown>[];
  ledger: Record<string, unknown>[];
  crop_intelligence: {
    most_cultivated_crop: string | null;
    average_yield: string | null;
    average_procurement_kg: string | null;
    preferred_buyer: string | null;
    preferred_selling_season: string | null;
    most_profitable_crop: string | null;
    procurement_frequency: number;
  };
  land: LandParcel[];
  documents: {
    id: string;
    document_type: string;
    file_name: string;
    mime_type: string;
    link_role: string | null;
    created_at: string | null;
  }[];
  communication: {
    id: string;
    kind: string;
    body: string;
    author_name: string | null;
    created_at: string;
  }[];
  analytics: {
    total_revenue: string;
    total_diesel_consumed: string;
    total_tractor_hours: string;
    total_trips: number;
    average_payment_delay_days: string | null;
    average_procurement_rate: string | null;
    average_service_cost: string | null;
    current_outstanding: string;
    season_wise_revenue: Record<string, string>;
    year_wise_revenue: Record<string, string>;
  };
  recommendations: {
    code: string;
    title: string;
    rationale: string;
    priority: string;
    action_href: string | null;
  }[];
  quick_actions: {
    code: string;
    label: string;
    href: string;
    category: string;
  }[];
  bank_accounts_count: number;
}

export type Farmer360Section =
  | "overview"
  | "timeline"
  | "services"
  | "farming"
  | "procurements"
  | "finance"
  | "ledger"
  | "land"
  | "documents"
  | "communication"
  | "analytics"
  | "actions";

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

export function fetchFarmer360(id: string): Promise<Farmer360Profile> {
  return fetchApi<Farmer360Profile>(`/farmers/${id}/profile-360`, {
    method: "GET",
    clientHeaders: false,
  });
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
    preferred_language: string | null;
    preferred_payment_cycle: string | null;
    preferred_payment_method: string | null;
    trust_rating: number | null;
    is_vip: boolean;
    geo_lat: string | null;
    geo_lng: string | null;
  }>,
): Promise<FarmerDetail> {
  return fetchApi<FarmerDetail>(`/farmers/${id}`, {
    method: "PATCH",
    body: payload,
    clientHeaders: true,
  });
}
