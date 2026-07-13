import { fetchApi } from "@/lib/api/client";

export type Village360Section =
  | "overview"
  | "farmers"
  | "procurements"
  | "services"
  | "vehicles"
  | "payments"
  | "finance"
  | "farming"
  | "buyers"
  | "comments"
  | "documents"
  | "analytics"
  | "timeline";

export interface Village360Profile {
  summary: {
    id: string;
    village_code: string | null;
    name: string;
    mandal: string | null;
    district: string | null;
    state: string | null;
    pincode: string | null;
    geo_lat: string | null;
    geo_lng: string | null;
    agent_id: string | null;
    agent_name: string | null;
    status: string;
    population: number | null;
    estimated_cultivable_area: string | null;
    notes: string | null;
  };
  statistics: Record<string, string | number>;
  farmers: Record<string, unknown>[];
  procurements: Record<string, unknown>[];
  services: Record<string, unknown>[];
  vehicles: Record<string, unknown>[];
  payments: Record<string, unknown>[];
  finance: Record<string, unknown>[];
  farming: Record<string, unknown>[];
  buyers: Record<string, unknown>[];
  comments: { id: string; body: string; author_name: string | null; created_at: string }[];
  documents: { id: string; document_type: string; file_name: string; mime_type: string }[];
  timeline: {
    event_type: string;
    title: string;
    description: string | null;
    occurred_at: string;
    amount: string | null;
  }[];
  analytics: {
    top_crop: string | null;
    top_farmer: string | null;
    top_buyer: string | null;
    most_used_vehicle: string | null;
    average_yield: string | null;
    average_procurement_rate: string | null;
    average_payment_delay_days: string | null;
    village_growth_farmers: number;
    revenue_trend: Record<string, string>;
    season_comparison: Record<string, string>;
  };
  map: {
    village_center: { lat: string | null; lng: string | null };
    farmer_locations_count: number;
    farm_locations_count: number;
    supports_boundary: boolean;
    supports_live_vehicles: boolean;
  };
  reports: { code: string; title: string; href: string; status: string }[];
}

export interface VillageSearchHit {
  id: string;
  village_code: string | null;
  name: string;
  mandal: string | null;
  district: string | null;
  match_reason: string;
  farmer_count: number;
}

export function fetchVillage360(id: string): Promise<Village360Profile> {
  return fetchApi<Village360Profile>(`/villages/${id}/profile-360`, {
    method: "GET",
    clientHeaders: false,
  });
}

export function searchVillages(q: string): Promise<{ items: VillageSearchHit[]; total: number; q: string }> {
  const params = new URLSearchParams({ q });
  return fetchApi(`/villages/search?${params}`, { method: "GET", clientHeaders: false });
}
