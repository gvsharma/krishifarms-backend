export const SERVICE_CATEGORIES = [
  { value: "field_service", label: "Field service" },
  { value: "tractor_work", label: "Tractor work" },
  { value: "transport", label: "Transport" },
  { value: "fertiliser", label: "Fertiliser" },
  { value: "seeds", label: "Seeds" },
  { value: "agri_finance", label: "Agri-finance" },
  { value: "vehicle_ops", label: "Vehicle ops" },
  { value: "godown", label: "Godown" },
] as const;

export type ServiceCategory = (typeof SERVICE_CATEGORIES)[number]["value"];

export const STATUS_OPTIONS = [
  { value: "open", label: "Open" },
  { value: "completed", label: "Completed" },
  { value: "cancelled", label: "Cancelled" },
] as const;

export const CLEANING_STATUS_OPTIONS = [
  { value: "pending", label: "Pending" },
  { value: "done", label: "Done" },
  { value: "not_required", label: "Not required" },
] as const;

export const FACILITY_STATUS_OPTIONS = [
  { value: "active", label: "Active" },
  { value: "repair", label: "Repair" },
  { value: "maintenance", label: "Maintenance" },
  { value: "cleaning", label: "Cleaning" },
] as const;

export type FieldKey =
  | "activity_type_id"
  | "vehicle_type_id"
  | "farmer_id"
  | "location"
  | "hours"
  | "diesel_amount"
  | "amount_given"
  | "advance_amount"
  | "total_amount"
  | "pending_amount"
  | "bag_count"
  | "quantity"
  | "quantity_unit"
  | "rate_per_unit"
  | "cleaning_status"
  | "facility_status";

/** Category-specific operational fields (common: date, status, comments always shown). */
export const CATEGORY_FIELDS: Record<ServiceCategory, FieldKey[]> = {
  field_service: [
    "farmer_id",
    "activity_type_id",
    "location",
    "hours",
    "diesel_amount",
    "amount_given",
    "advance_amount",
    "total_amount",
    "pending_amount",
  ],
  tractor_work: [
    "farmer_id",
    "activity_type_id",
    "vehicle_type_id",
    "location",
    "hours",
    "diesel_amount",
    "advance_amount",
    "total_amount",
    "pending_amount",
  ],
  transport: [
    "farmer_id",
    "activity_type_id",
    "vehicle_type_id",
    "location",
    "advance_amount",
    "total_amount",
    "pending_amount",
  ],
  fertiliser: ["farmer_id", "bag_count", "advance_amount", "total_amount", "pending_amount"],
  seeds: [
    "farmer_id",
    "quantity",
    "quantity_unit",
    "rate_per_unit",
    "advance_amount",
    "total_amount",
    "pending_amount",
  ],
  agri_finance: ["farmer_id", "amount_given", "total_amount", "pending_amount"],
  vehicle_ops: [
    "activity_type_id",
    "vehicle_type_id",
    "location",
    "cleaning_status",
    "facility_status",
    "advance_amount",
    "total_amount",
    "pending_amount",
  ],
  godown: [
    "activity_type_id",
    "location",
    "cleaning_status",
    "facility_status",
    "advance_amount",
    "total_amount",
    "pending_amount",
  ],
};

export function categoryLabel(value: string): string {
  return SERVICE_CATEGORIES.find((c) => c.value === value)?.label ?? value.replace(/_/g, " ");
}
