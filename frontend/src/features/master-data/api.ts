import { fetchApi } from "@/lib/api/client";

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface Village {
  id: string;
  org_id: string;
  name: string;
  mandal: string | null;
  district: string | null;
  state: string | null;
  pincode: string | null;
  created_at: string;
  updated_at: string;
}

export interface CropType {
  id: string;
  org_id: string;
  name: string;
  code: string;
  default_moisture_pct: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ExpenseCategory {
  id: string;
  org_id: string;
  name: string;
  parent_id: string | null;
  type: string;
  created_at: string;
  updated_at: string;
}

export interface Buyer {
  id: string;
  name: string;
  name_te: string | null;
  phone: string | null;
  gstin: string | null;
  contact_person: string | null;
  address: string | null;
  village_id: string | null;
  notes: string | null;
  is_active: boolean;
}

export interface FieldAgent {
  id: string;
  name: string;
  name_te: string | null;
  phone: string | null;
  user_id: string | null;
  village_id: string | null;
  commission_pct: string | null;
  notes: string | null;
  is_active: boolean;
}

export interface VehicleType {
  id: string;
  name: string;
  name_te: string | null;
  code: string;
  capacity_quintals: string | null;
  fuel_type: string | null;
  notes: string | null;
  is_active: boolean;
}

export interface ActivityType {
  id: string;
  name: string;
  name_te: string | null;
  code: string;
  service_category: string | null;
  default_rate_type: string | null;
  is_active: boolean;
}

export interface PaymentMode {
  id: string;
  code: string;
  name: string;
  name_te: string | null;
  is_active: boolean;
}

export interface CropPrice {
  id: string;
  crop_type_id: string;
  village_id: string | null;
  effective_from: string;
  effective_to: string | null;
  rate_per_quintal: string;
  notes: string | null;
  is_active: boolean;
}

function pageParams(page = 1, pageSize = 50): string {
  return new URLSearchParams({ page: String(page), page_size: String(pageSize) }).toString();
}

/* Villages */
export function fetchVillages(page = 1, pageSize = 50): Promise<Paginated<Village>> {
  return fetchApi(`/villages?${pageParams(page, pageSize)}`, { method: "GET", clientHeaders: false });
}
export function createVillage(payload: {
  name: string;
  mandal?: string | null;
  district?: string | null;
  state?: string | null;
  pincode?: string | null;
}): Promise<Village> {
  return fetchApi("/villages", { method: "POST", body: payload, clientHeaders: true });
}
export function updateVillage(
  id: string,
  payload: Partial<{
    name: string;
    mandal: string | null;
    district: string | null;
    state: string | null;
    pincode: string | null;
  }>,
): Promise<Village> {
  return fetchApi(`/villages/${id}`, { method: "PATCH", body: payload, clientHeaders: true });
}
export function deleteVillage(id: string): Promise<{ message: string }> {
  return fetchApi(`/villages/${id}`, { method: "DELETE", clientHeaders: true });
}

/* Crop types */
export function fetchCropTypes(page = 1, pageSize = 50): Promise<Paginated<CropType>> {
  return fetchApi(`/crop-types?${pageParams(page, pageSize)}`, { method: "GET", clientHeaders: false });
}
export function createCropType(payload: {
  name: string;
  code: string;
  default_moisture_pct?: number | null;
  is_active?: boolean;
}): Promise<CropType> {
  return fetchApi("/crop-types", { method: "POST", body: payload, clientHeaders: true });
}
export function updateCropType(
  id: string,
  payload: Partial<{
    name: string;
    code: string;
    default_moisture_pct: number | null;
    is_active: boolean;
  }>,
): Promise<CropType> {
  return fetchApi(`/crop-types/${id}`, { method: "PATCH", body: payload, clientHeaders: true });
}
export function deleteCropType(id: string): Promise<{ message: string }> {
  return fetchApi(`/crop-types/${id}`, { method: "DELETE", clientHeaders: true });
}

/* Expense categories */
export function fetchExpenseCategories(page = 1, pageSize = 50): Promise<Paginated<ExpenseCategory>> {
  return fetchApi(`/expense-categories?${pageParams(page, pageSize)}`, {
    method: "GET",
    clientHeaders: false,
  });
}
export function createExpenseCategory(payload: {
  name: string;
  parent_id?: string | null;
  type?: string;
}): Promise<ExpenseCategory> {
  return fetchApi("/expense-categories", { method: "POST", body: payload, clientHeaders: true });
}
export function updateExpenseCategory(
  id: string,
  payload: Partial<{ name: string; parent_id: string | null; type: string }>,
): Promise<ExpenseCategory> {
  return fetchApi(`/expense-categories/${id}`, { method: "PATCH", body: payload, clientHeaders: true });
}
export function deleteExpenseCategory(id: string): Promise<{ message: string }> {
  return fetchApi(`/expense-categories/${id}`, { method: "DELETE", clientHeaders: true });
}

/* Buyers */
export function fetchBuyers(page = 1, pageSize = 50): Promise<Paginated<Buyer>> {
  return fetchApi(`/buyers?${pageParams(page, pageSize)}`, { method: "GET", clientHeaders: false });
}
export function createBuyer(payload: Record<string, unknown>): Promise<Buyer> {
  return fetchApi("/buyers", { method: "POST", body: payload, clientHeaders: true });
}
export function updateBuyer(id: string, payload: Record<string, unknown>): Promise<Buyer> {
  return fetchApi(`/buyers/${id}`, { method: "PATCH", body: payload, clientHeaders: true });
}
export function deleteBuyer(id: string): Promise<{ message: string }> {
  return fetchApi(`/buyers/${id}`, { method: "DELETE", clientHeaders: true });
}

/* Field agents */
export function fetchAgents(page = 1, pageSize = 50): Promise<Paginated<FieldAgent>> {
  return fetchApi(`/agents?${pageParams(page, pageSize)}`, { method: "GET", clientHeaders: false });
}
export function createAgent(payload: Record<string, unknown>): Promise<FieldAgent> {
  return fetchApi("/agents", { method: "POST", body: payload, clientHeaders: true });
}
export function updateAgent(id: string, payload: Record<string, unknown>): Promise<FieldAgent> {
  return fetchApi(`/agents/${id}`, { method: "PATCH", body: payload, clientHeaders: true });
}
export function deleteAgent(id: string): Promise<{ message: string }> {
  return fetchApi(`/agents/${id}`, { method: "DELETE", clientHeaders: true });
}

/* Vehicle types */
export function fetchVehicleTypes(page = 1, pageSize = 50): Promise<Paginated<VehicleType>> {
  return fetchApi(`/vehicle-types?${pageParams(page, pageSize)}`, { method: "GET", clientHeaders: false });
}
export function createVehicleType(payload: Record<string, unknown>): Promise<VehicleType> {
  return fetchApi("/vehicle-types", { method: "POST", body: payload, clientHeaders: true });
}
export function updateVehicleType(id: string, payload: Record<string, unknown>): Promise<VehicleType> {
  return fetchApi(`/vehicle-types/${id}`, { method: "PATCH", body: payload, clientHeaders: true });
}
export function deleteVehicleType(id: string): Promise<{ message: string }> {
  return fetchApi(`/vehicle-types/${id}`, { method: "DELETE", clientHeaders: true });
}

/* Activity types */
export function fetchActivityTypes(page = 1, pageSize = 50): Promise<Paginated<ActivityType>> {
  return fetchApi(`/activity-types?${pageParams(page, pageSize)}`, { method: "GET", clientHeaders: false });
}
export function createActivityType(payload: Record<string, unknown>): Promise<ActivityType> {
  return fetchApi("/activity-types", { method: "POST", body: payload, clientHeaders: true });
}
export function updateActivityType(id: string, payload: Record<string, unknown>): Promise<ActivityType> {
  return fetchApi(`/activity-types/${id}`, { method: "PATCH", body: payload, clientHeaders: true });
}
export function deleteActivityType(id: string): Promise<{ message: string }> {
  return fetchApi(`/activity-types/${id}`, { method: "DELETE", clientHeaders: true });
}

/* Payment modes */
export function fetchPaymentModes(page = 1, pageSize = 50): Promise<Paginated<PaymentMode>> {
  return fetchApi(`/payment-modes?${pageParams(page, pageSize)}`, { method: "GET", clientHeaders: false });
}
export function createPaymentMode(payload: Record<string, unknown>): Promise<PaymentMode> {
  return fetchApi("/payment-modes", { method: "POST", body: payload, clientHeaders: true });
}
export function updatePaymentMode(id: string, payload: Record<string, unknown>): Promise<PaymentMode> {
  return fetchApi(`/payment-modes/${id}`, { method: "PATCH", body: payload, clientHeaders: true });
}
export function deletePaymentMode(id: string): Promise<{ message: string }> {
  return fetchApi(`/payment-modes/${id}`, { method: "DELETE", clientHeaders: true });
}

/* Crop prices */
export function fetchCropPrices(page = 1, pageSize = 50): Promise<Paginated<CropPrice>> {
  return fetchApi(`/crop-prices?${pageParams(page, pageSize)}`, { method: "GET", clientHeaders: false });
}
export function createCropPrice(payload: Record<string, unknown>): Promise<CropPrice> {
  return fetchApi("/crop-prices", { method: "POST", body: payload, clientHeaders: true });
}
export function updateCropPrice(id: string, payload: Record<string, unknown>): Promise<CropPrice> {
  return fetchApi(`/crop-prices/${id}`, { method: "PATCH", body: payload, clientHeaders: true });
}
export function deleteCropPrice(id: string): Promise<{ message: string }> {
  return fetchApi(`/crop-prices/${id}`, { method: "DELETE", clientHeaders: true });
}
