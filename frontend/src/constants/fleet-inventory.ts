/** KrishiFarms fleet inventory — mirrors scripts/data/fleet_inventory.py */

export interface FleetCatalogItem {
  code: string;
  name: string;
  nameTe: string;
  fuelType: "tractor" | "diesel" | "implement";
}

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

export const FLEET_IMPLEMENTS: FleetCatalogItem[] = [
  { code: "TROLLEY", name: "Trolley", nameTe: "ట్రాలీ", fuelType: "implement" },
  { code: "BALER", name: "Baler", nameTe: "బేలర్", fuelType: "implement" },
  { code: "PUMP", name: "Pump", nameTe: "పంపు", fuelType: "implement" },
  { code: "CULTIVATOR", name: "Cultivator", nameTe: "కల్టివేటర్", fuelType: "implement" },
  { code: "ROTAVATOR", name: "Rotavator", nameTe: "రోటవేటర్", fuelType: "implement" },
  { code: "WEEDER", name: "Weeder", nameTe: "వీడర్", fuelType: "implement" },
];

export const FLEET_LEGACY_CODES = ["BOLERO", "DCM"] as const;

export const FUEL_TYPE_OPTIONS = [
  { value: "tractor", label: "Tractor" },
  { value: "diesel", label: "Diesel vehicle" },
  { value: "implement", label: "Implement / attachment" },
] as const;

export const FLEET_INVENTORY_SUMMARY =
  "John Deere tractors (2W, 4W), Mahindra Bolero, Eicher DCM, and implements (trolley, baler, pump, cultivator, rotavator, weeder)";

export const TRACTOR_WORK_VEHICLE_CODES = new Set([
  ...FLEET_TRACTORS.map((v) => v.code),
  ...FLEET_IMPLEMENTS.map((v) => v.code),
]);

export const TRANSPORT_VEHICLE_CODES = new Set([
  ...FLEET_TRANSPORT.map((v) => v.code),
  ...FLEET_LEGACY_CODES,
]);

export const FLEET_VEHICLE_ORDER = [
  ...FLEET_TRACTORS.map((v) => v.code),
  ...FLEET_TRANSPORT.map((v) => v.code),
  ...FLEET_IMPLEMENTS.map((v) => v.code),
  ...FLEET_LEGACY_CODES,
];

interface VehicleLike {
  code: string;
  is_active?: boolean;
}

export function filterVehiclesForCategory<T extends VehicleLike>(
  category: string,
  vehicles: T[],
): T[] {
  const active = vehicles.filter((v) => v.is_active !== false);
  if (category === "transport") {
    return active.filter((v) => TRANSPORT_VEHICLE_CODES.has(v.code));
  }
  if (category === "tractor_work") {
    return active.filter((v) => TRACTOR_WORK_VEHICLE_CODES.has(v.code));
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
