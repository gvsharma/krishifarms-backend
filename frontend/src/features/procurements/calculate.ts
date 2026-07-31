/** Client-side mirror of backend procurement calculate preview (Decimal-safe enough for UI). */

export interface ProcurementCalcInput {
  bagCount: number;
  /** Uniform weight — ignored when bagWeightsKg is provided. */
  weightPerBagKg?: number;
  /** Per-bag weights; gross = sum when provided. */
  bagWeightsKg?: number[];
  perBagDeductionKg: number;
  tareWeightKg?: number;
  ratePerQuintal: number;
  isSpotPayment?: boolean;
  spotDeductionPerQuintal?: number;
  lineDeductionAmount?: number;
}

export interface ProcurementCalcResult {
  grossWeightKg: number;
  bagWeightDeductionKg: number;
  netWeightKg: number;
  netQuintals: number;
  grossAmount: number;
  lineDeductionAmount: number;
  spotDeductionAmount: number;
  netAmount: number;
}

const QUINTAL_KG = 100;

function round2(n: number): number {
  return Math.round(n * 100) / 100;
}

function round3(n: number): number {
  return Math.round(n * 1000) / 1000;
}

export function calculateProcurementPreview(input: ProcurementCalcInput): ProcurementCalcResult | null {
  const bags = input.bagCount;
  const rate = input.ratePerQuintal;
  if (bags <= 0 || rate <= 0) return null;

  let grossWeightKg: number;
  if (input.bagWeightsKg && input.bagWeightsKg.length === bags) {
    const valid = input.bagWeightsKg.every((w) => w > 0);
    if (!valid) return null;
    grossWeightKg = round3(input.bagWeightsKg.reduce((a, b) => a + b, 0));
  } else {
    const weightPerBag = input.weightPerBagKg ?? 0;
    if (weightPerBag <= 0) return null;
    grossWeightKg = round3(bags * weightPerBag);
  }

  const perBagDeduction = input.perBagDeductionKg ?? 2;
  const tare = input.tareWeightKg ?? 0;
  const bagWeightDeductionKg = round3(bags * perBagDeduction);
  const netWeightKg = round3(grossWeightKg - tare - bagWeightDeductionKg);
  if (netWeightKg <= 0) return null;

  const netQuintals = round3(netWeightKg / QUINTAL_KG);
  const grossAmount = round2(netQuintals * rate);
  const lineDeductionAmount = round2(input.lineDeductionAmount ?? 0);
  const spotRate = input.spotDeductionPerQuintal ?? 100;
  const spotDeductionAmount =
    input.isSpotPayment && spotRate > 0 ? round2(netQuintals * spotRate) : 0;
  const netAmount = round2(grossAmount - lineDeductionAmount - spotDeductionAmount);
  if (netAmount < 0) return null;

  return {
    grossWeightKg,
    bagWeightDeductionKg,
    netWeightKg,
    netQuintals,
    grossAmount,
    lineDeductionAmount,
    spotDeductionAmount,
    netAmount,
  };
}
