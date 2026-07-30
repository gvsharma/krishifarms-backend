/** KrishiFarms fleet inventory — mirrors scripts/data/fleet_inventory.py */

export interface FleetCatalogItem {
  code: string;
  name: string;
  nameTe: string;
  fuelType: "tractor" | "diesel" | "implement";
}

/** Ops dropdown types: Tractor … Drone */
export const FLEET_SERVICE_TYPES: FleetCatalogItem[] = [
  { code: "TRACTOR", name: "Tractor", nameTe: "ట్రాక్టర్", fuelType: "tractor" },
  { code: "CULTIVATOR", name: "Cultivator", nameTe: "కల్టివేటర్", fuelType: "implement" },
  { code: "ROTAVATOR", name: "Rotavator", nameTe: "రోటవేటర్", fuelType: "implement" },
  { code: "BALER", name: "Baler", nameTe: "బేలర్", fuelType: "implement" },
  { code: "TROLLEY", name: "Trolley", nameTe: "ట్రాలీ", fuelType: "implement" },
  { code: "WEEDER", name: "Weeder", nameTe: "వీడర్", fuelType: "implement" },
  {
    code: "FERTILIZER_PUMP",
    name: "Fertilizer Pump",
    nameTe: "ఎరువు పంపు",
    fuelType: "implement",
  },
  { code: "BOLERO", name: "Bolero", nameTe: "బోలేరో", fuelType: "diesel" },
  { code: "DCM", name: "DCM", nameTe: "డీసీఎం", fuelType: "diesel" },
  { code: "HARVESTER", name: "Harvester", nameTe: "హార్వెస్టర్", fuelType: "diesel" },
  { code: "DRONE", name: "Drone", nameTe: "డ్రోన్", fuelType: "implement" },
];

export const FLEET_TRACTORS: FleetCatalogItem[] = [
  {
    code: "JD_TRACTOR_2W",
    name: "John Deere tractor 2W",
    nameTe: "జాన్ డియర్ ట్రాక్టర్ 2W",
    fuelType: "tractor",
  },
  {
    code: "JD_TRACTOR_4W",
    name: "John Deere tractor 4W",
    nameTe: "జాన్ డియర్ ట్రాక్టర్ 4W",
    fuelType: "tractor",
  },
];

export const FLEET_TRANSPORT: FleetCatalogItem[] = [
  {
    code: "MAHINDRA_BOLERO",
    name: "Mahindra Bolero",
    nameTe: "మహీంద్రా బోలేరో",
    fuelType: "diesel",
  },
  {
    code: "EICHER_DCM",
    name: "Eicher DCM",
    nameTe: "ఐషర్ డీసీఎం",
    fuelType: "diesel",
  },
];

export const FLEET_IMPLEMENTS: FleetCatalogItem[] = FLEET_SERVICE_TYPES.filter((v) =>
  ["TROLLEY", "BALER", "FERTILIZER_PUMP", "CULTIVATOR", "ROTAVATOR", "WEEDER"].includes(v.code),
);

export const FLEET_LEGACY_CODES = ["PUMP"] as const;

export const FUEL_TYPE_OPTIONS = [
  { value: "tractor", label: "Tractor" },
  { value: "diesel", label: "Diesel vehicle" },
  { value: "implement", label: "Implement / attachment" },
] as const;

export const FLEET_INVENTORY_SUMMARY =
  "Tractor, Cultivator, Rotavator, Baler, Trolley, Weeder, Fertilizer Pump, Bolero, DCM, Harvester, Drone — plus John Deere 2W/4W, Mahindra Bolero, Eicher DCM";

export const TRACTOR_WORK_VEHICLE_CODES = new Set([
  "TRACTOR",
  "CULTIVATOR",
  "ROTAVATOR",
  "BALER",
  "TROLLEY",
  "WEEDER",
  "FERTILIZER_PUMP",
  "HARVESTER",
  "DRONE",
  "PUMP",
  ...FLEET_TRACTORS.map((v) => v.code),
]);

export const TRANSPORT_VEHICLE_CODES = new Set([
  "BOLERO",
  "DCM",
  ...FLEET_TRANSPORT.map((v) => v.code),
]);

export const FLEET_VEHICLE_ORDER = [
  ...FLEET_SERVICE_TYPES.map((v) => v.code),
  ...FLEET_TRACTORS.map((v) => v.code),
  ...FLEET_TRANSPORT.map((v) => v.code),
  ...FLEET_LEGACY_CODES,
];

/** Vehicle-specific work form profile (conditional questions). */
export type VehicleWorkProfile =
  | "tractor"
  | "trolley"
  | "bolero"
  | "dcm"
  | "pump"
  | "drone"
  | "baler"
  | null;

/** Farming implements share tractor-style crop/area/stage questions. */
const TRACTOR_PROFILE_CODES = new Set([
  "TRACTOR",
  "JD_TRACTOR_2W",
  "JD_TRACTOR_4W",
  "CULTIVATOR",
  "ROTAVATOR",
  "WEEDER",
  "HARVESTER",
]);
const BALER_PROFILE_CODES = new Set(["BALER"]);
const TROLLEY_PROFILE_CODES = new Set(["TROLLEY"]);
const BOLERO_PROFILE_CODES = new Set(["BOLERO", "MAHINDRA_BOLERO"]);
const DCM_PROFILE_CODES = new Set(["DCM", "EICHER_DCM"]);
const PUMP_PROFILE_CODES = new Set(["FERTILIZER_PUMP", "PUMP"]);
const DRONE_PROFILE_CODES = new Set(["DRONE"]);

export function resolveVehicleWorkProfile(
  code: string | undefined | null,
  fuelType?: string | null,
): VehicleWorkProfile {
  if (!code) return null;
  const c = code.toUpperCase();
  if (BALER_PROFILE_CODES.has(c)) return "baler";
  if (TRACTOR_PROFILE_CODES.has(c)) return "tractor";
  if (TROLLEY_PROFILE_CODES.has(c)) return "trolley";
  if (BOLERO_PROFILE_CODES.has(c)) return "bolero";
  if (DCM_PROFILE_CODES.has(c)) return "dcm";
  if (PUMP_PROFILE_CODES.has(c)) return "pump";
  if (DRONE_PROFILE_CODES.has(c)) return "drone";

  // Custom master-data codes (e.g. tractor4W) — infer from code / fuel_type.
  if (c.includes("TROLLEY")) return "trolley";
  if (c.includes("BOLERO")) return "bolero";
  if (c.includes("DCM")) return "dcm";
  if (c.includes("DRONE")) return "drone";
  if (c.includes("PUMP")) return "pump";
  if (c.includes("BALER")) return "baler";
  if (
    c.includes("TRACTOR") ||
    c.includes("CULTIVATOR") ||
    c.includes("ROTAVATOR") ||
    c.includes("WEEDER") ||
    c.includes("HARVESTER") ||
    /[24]W/.test(c)
  ) {
    return "tractor";
  }
  const fuel = (fuelType ?? "").toLowerCase();
  if (fuel === "tractor" || fuel === "implement") return "tractor";
  if (fuel === "diesel") {
    if (c.includes("BOLERO")) return "bolero";
    if (c.includes("DCM")) return "dcm";
  }
  return null;
}

interface VehicleLike {
  code: string;
  is_active?: boolean;
  fuel_type?: string | null;
}

function codeInSet(code: string, set: Set<string>): boolean {
  return set.has(code) || set.has(code.toUpperCase());
}

/** True when a custom vehicle type belongs in tractor / implement work lists. */
function isTractorWorkCustom(v: VehicleLike): boolean {
  const fuel = (v.fuel_type ?? "").toLowerCase();
  if (fuel === "tractor" || fuel === "implement") return true;
  if (fuel === "diesel") return false;
  const c = v.code.toUpperCase();
  return (
    c.includes("TRACTOR") ||
    c.includes("CULTIVATOR") ||
    c.includes("ROTAVATOR") ||
    c.includes("BALER") ||
    c.includes("WEEDER") ||
    c.includes("HARVESTER") ||
    c.includes("TROLLEY") ||
    c.includes("PUMP") ||
    c.includes("DRONE") ||
    /[24]W/.test(c)
  );
}

function isTransportCustom(v: VehicleLike): boolean {
  const fuel = (v.fuel_type ?? "").toLowerCase();
  if (fuel === "diesel") return true;
  if (fuel === "tractor" || fuel === "implement") return false;
  const c = v.code.toUpperCase();
  return c.includes("BOLERO") || c.includes("DCM");
}

export function filterVehiclesForCategory<T extends VehicleLike>(
  category: string,
  vehicles: T[],
): T[] {
  const active = vehicles.filter((v) => v.is_active !== false);
  if (category === "transport") {
    return active.filter(
      (v) => codeInSet(v.code, TRANSPORT_VEHICLE_CODES) || isTransportCustom(v),
    );
  }
  if (category === "tractor_work") {
    return active.filter(
      (v) => codeInSet(v.code, TRACTOR_WORK_VEHICLE_CODES) || isTractorWorkCustom(v),
    );
  }
  if (category === "vehicle_ops") {
    return active;
  }
  return active;
}

export function sortFleetVehicles<T extends VehicleLike>(vehicles: T[]): T[] {
  const order = new Map(FLEET_VEHICLE_ORDER.map((code, index) => [code, index]));
  return [...vehicles].sort((a, b) => {
    const ai = order.get(a.code) ?? 999;
    const bi = order.get(b.code) ?? 999;
    if (ai !== bi) return ai - bi;
    return a.code.localeCompare(b.code);
  });
}
