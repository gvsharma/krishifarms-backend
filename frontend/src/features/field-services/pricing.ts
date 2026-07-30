/** Default implement billing rates (INR) — mirrors scripts/data/fleet_inventory.py */

export type RateUnit = "hour" | "trip" | "bale";

export interface ImplementRate {
  default_rate: string;
  default_rate_unit: RateUnit;
}

export const IMPLEMENT_DEFAULT_RATES: Record<string, ImplementRate> = {
  CULTIVATOR: { default_rate: "1200", default_rate_unit: "hour" },
  ROTAVATOR: { default_rate: "1440", default_rate_unit: "hour" },
  TROLLEY: { default_rate: "250", default_rate_unit: "trip" },
  BALER: { default_rate: "40", default_rate_unit: "bale" },
  WEEDER: { default_rate: "1000", default_rate_unit: "hour" },
  FERTILIZER_PUMP: { default_rate: "500", default_rate_unit: "hour" },
  PUMP: { default_rate: "500", default_rate_unit: "hour" },
};

export interface VehicleRateLike {
  code: string;
  default_rate?: string | null;
  default_rate_unit?: RateUnit | string | null;
}

export function resolveVehicleRate(vehicle: VehicleRateLike | null | undefined): ImplementRate | null {
  if (!vehicle) return null;
  if (vehicle.default_rate && vehicle.default_rate_unit) {
    return {
      default_rate: vehicle.default_rate,
      default_rate_unit: vehicle.default_rate_unit as RateUnit,
    };
  }
  return IMPLEMENT_DEFAULT_RATES[vehicle.code.toUpperCase()] ?? null;
}

export function computeVehicleCharge(
  rate: ImplementRate | null,
  input: { hours?: string; trips?: string; baleCount?: string },
): { ratePerUnit: string; total: string } | null {
  if (!rate) return null;
  const unitRate = Number(rate.default_rate);
  if (!Number.isFinite(unitRate) || unitRate < 0) return null;

  let qty = 0;
  if (rate.default_rate_unit === "hour") {
    qty = Number(input.hours);
  } else if (rate.default_rate_unit === "trip") {
    qty = Number(input.trips);
  } else if (rate.default_rate_unit === "bale") {
    qty = Number(input.baleCount);
  }
  if (!Number.isFinite(qty) || qty <= 0) {
    return { ratePerUnit: rate.default_rate, total: "0.00" };
  }

  const total = (unitRate * qty).toFixed(2);
  return { ratePerUnit: rate.default_rate, total };
}

export function rateUnitLabel(unit: RateUnit): string {
  switch (unit) {
    case "hour":
      return "per hour";
    case "trip":
      return "per trip";
    case "bale":
      return "per bale";
    default:
      return unit;
  }
}
