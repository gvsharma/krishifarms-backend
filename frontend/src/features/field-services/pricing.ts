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

/** Combine whole hours + minutes into decimal hours for API (`hours` column). */
export function decimalHoursFromParts(hours: string, minutes: string): string {
  const h = Number(hours);
  const m = Number(minutes);
  const whole = Number.isFinite(h) && h > 0 ? h : 0;
  const mins = Number.isFinite(m) && m > 0 ? m : 0;
  if (mins >= 60) return whole.toFixed(2);
  return (whole + mins / 60).toFixed(2);
}

export function partsFromDecimalHours(decimal: string): { hours: string; minutes: string } {
  const n = Number(decimal);
  if (!Number.isFinite(n) || n <= 0) return { hours: "", minutes: "" };
  const wholeHours = Math.floor(n);
  let mins = Math.round((n - wholeHours) * 60);
  let hours = wholeHours;
  if (mins === 60) {
    hours += 1;
    mins = 0;
  }
  return { hours: String(hours), minutes: mins > 0 ? String(mins) : "" };
}

export function computeBillingTotal(
  rate: ImplementRate | null,
  input: {
    ratePerUnit?: string;
    hours?: string;
    workHours?: string;
    workMinutes?: string;
    trips?: string;
    baleCount?: string;
  },
): string | null {
  if (!rate) return null;
  const unitRate = Number(input.ratePerUnit ?? rate.default_rate);
  if (!Number.isFinite(unitRate) || unitRate < 0) return null;

  let qty = 0;
  if (rate.default_rate_unit === "hour") {
    if (input.workHours !== undefined || input.workMinutes !== undefined) {
      qty = Number(decimalHoursFromParts(input.workHours ?? "", input.workMinutes ?? ""));
    } else {
      qty = Number(input.hours);
    }
  } else if (rate.default_rate_unit === "trip") {
    qty = Number(input.trips);
  } else if (rate.default_rate_unit === "bale") {
    qty = Number(input.baleCount);
  }
  if (!Number.isFinite(qty) || qty <= 0) return "0.00";
  return (unitRate * qty).toFixed(2);
}

export function computePendingTotal(total: string, advance: string): string {
  const t = Number(total);
  const a = Number(advance);
  if (!Number.isFinite(t) || t < 0) return "0.00";
  const adv = Number.isFinite(a) && a > 0 ? a : 0;
  return Math.max(0, t - adv).toFixed(2);
}

export function computeVehicleCharge(
  rate: ImplementRate | null,
  input: { hours?: string; trips?: string; baleCount?: string },
  ratePerUnitOverride?: string,
): { ratePerUnit: string; total: string } | null {
  if (!rate) return null;
  const total = computeBillingTotal(rate, {
    ratePerUnit: ratePerUnitOverride ?? rate.default_rate,
    hours: input.hours,
    trips: input.trips,
    baleCount: input.baleCount,
  });
  if (total === null) return null;
  return {
    ratePerUnit: ratePerUnitOverride ?? rate.default_rate,
    total,
  };
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
