"use client";

import { Card, Divider, Stack, Typography } from "@mui/material";
import type { ProcurementCalcResult } from "./calculate";
import { formatInr } from "./api";

export type ProcurementIntakeSummaryProps = {
  preview: ProcurementCalcResult | null;
  bagCount: number;
  ratePerQuintal: number;
  isSpotPayment: boolean;
  perBagDeductionKg: number;
};

function fmtKg(n: number): string {
  return `${n.toLocaleString("en-IN", { maximumFractionDigits: 3 })} kg`;
}

function fmtQtl(n: number): string {
  return `${n.toLocaleString("en-IN", { maximumFractionDigits: 3 })} qtl`;
}

export function ProcurementIntakeSummary({
  preview,
  bagCount,
  ratePerQuintal,
  isSpotPayment,
  perBagDeductionKg,
}: ProcurementIntakeSummaryProps) {
  if (!preview || ratePerQuintal <= 0 || bagCount <= 0) {
    return (
      <Card variant="outlined" sx={{ p: 2 }}>
        <Typography variant="subtitle1" fontWeight={600} gutterBottom>
          Final summary
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Enter bag weights and rate to see gross/net weights and payment totals.
        </Typography>
      </Card>
    );
  }

  return (
    <Card variant="outlined" sx={{ p: 2, bgcolor: "action.hover" }}>
      <Typography variant="subtitle1" fontWeight={600} gutterBottom>
        Final summary
      </Typography>

      <Typography variant="overline" color="text.secondary" display="block" sx={{ mt: 1 }}>
        Weights
      </Typography>
      <Stack spacing={0.5} sx={{ mb: 1.5 }}>
        <Row label="Bag count" value={String(bagCount)} />
        <Row label="Gross total weight" value={fmtKg(preview.grossWeightKg)} highlight />
        <Row
          label={`Weight deduction (kata ${perBagDeductionKg} kg/bag)`}
          value={`−${fmtKg(preview.bagWeightDeductionKg)}`}
        />
        <Row label="Net weight (payable)" value={fmtKg(preview.netWeightKg)} highlight />
        <Row label="Net quintals" value={fmtQtl(preview.netQuintals)} />
      </Stack>

      <Divider sx={{ my: 1.5 }} />

      <Typography variant="overline" color="text.secondary" display="block">
        Amounts
      </Typography>
      <Stack spacing={0.5}>
        <Row
          label={`Gross amount (${fmtQtl(preview.netQuintals)} × ${formatInr(ratePerQuintal)}/qtl)`}
          value={formatInr(preview.grossAmount)}
          highlight
        />
        {preview.lineDeductionAmount > 0 && (
          <Row label="Line deductions" value={`−${formatInr(preview.lineDeductionAmount)}`} />
        )}
        {isSpotPayment && preview.spotDeductionAmount > 0 && (
          <Row label="Spot payment deduction" value={`−${formatInr(preview.spotDeductionAmount)}`} />
        )}
        <Row label="Net payment to farmer" value={formatInr(preview.netAmount)} emphasis />
      </Stack>
    </Card>
  );
}

function Row({
  label,
  value,
  highlight,
  emphasis,
}: {
  label: string;
  value: string;
  highlight?: boolean;
  emphasis?: boolean;
}) {
  return (
    <Stack direction="row" justifyContent="space-between" alignItems="baseline" gap={2}>
      <Typography variant="body2" color={emphasis ? "text.primary" : "text.secondary"}>
        {label}
      </Typography>
      <Typography
        variant="body2"
        fontWeight={emphasis ? 700 : highlight ? 600 : 400}
        color={emphasis ? "primary.main" : undefined}
        textAlign="right"
      >
        {value}
      </Typography>
    </Stack>
  );
}
