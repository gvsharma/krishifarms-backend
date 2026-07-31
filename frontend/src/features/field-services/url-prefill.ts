import type { ServiceCategory } from "./constants";

/** Farmer 360 quick-action `vehicle` query param → vehicle_types.code */
export const VEHICLE_SLUG_TO_CODE: Record<string, string> = {
  tractor: "TRACTOR",
  rotavator: "ROTAVATOR",
  cultivator: "CULTIVATOR",
  trolley: "TROLLEY",
  bolero: "BOLERO",
  dcm: "DCM",
  baler: "BALER",
  weeder: "WEEDER",
  fertilizer_pump: "FERTILIZER_PUMP",
};

export function categoryForVehicleSlug(slug: string | null | undefined): ServiceCategory {
  if (!slug) return "tractor_work";
  const key = slug.toLowerCase();
  if (key === "bolero" || key === "dcm") return "transport";
  return "tractor_work";
}

export function vehicleCodeFromSlug(slug: string | null | undefined): string | null {
  if (!slug) return null;
  return VEHICLE_SLUG_TO_CODE[slug.toLowerCase()] ?? slug.toUpperCase();
}
