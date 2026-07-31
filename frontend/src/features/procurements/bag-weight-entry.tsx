"use client";

import {
  Box,
  Button,
  Card,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { ContentCopy } from "@mui/icons-material";
import { TOUCH_FIELD_SX } from "@/lib/ui/touch-targets";
import { sumBagWeightsKg } from "./bag-weights";

export type BagWeightEntryProps = {
  bagWeights: string[];
  onChange: (weights: string[]) => void;
  perBagDeductionKg: string;
  disabled?: boolean;
};

export function BagWeightEntry({
  bagWeights,
  onChange,
  perBagDeductionKg,
  disabled = false,
}: BagWeightEntryProps) {
  const grossSum = sumBagWeightsKg(bagWeights);
  const kataPerBag = Number(perBagDeductionKg) || 2;
  const kataTotal = bagWeights.length * kataPerBag;

  const fillAll = (value: string) => {
    if (!value.trim()) return;
    onChange(bagWeights.map(() => value.trim()));
  };

  return (
    <Card variant="outlined" sx={{ p: 2, height: "100%" }}>
      <Stack spacing={1.5}>
        <Box>
          <Typography variant="subtitle1" fontWeight={600}>
            Bag weighment
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Enter each bag&apos;s weight (kg). Matches mobile per-bag intake.
          </Typography>
        </Box>

        {bagWeights.length === 0 ? (
          <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
            Set bag count first to list each bag.
          </Typography>
        ) : (
          <>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              <TextField
                size="small"
                label="Fill all (kg)"
                type="number"
                sx={{ ...TOUCH_FIELD_SX, minWidth: 120, flex: 1 }}
                inputProps={{ min: 0, step: 0.001 }}
                placeholder="50"
                disabled={disabled}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    fillAll((e.target as HTMLInputElement).value);
                  }
                }}
              />
              <Button
                size="small"
                variant="outlined"
                startIcon={<ContentCopy />}
                disabled={disabled || bagWeights.length === 0}
                onClick={() => {
                  const first = bagWeights.find((w) => Number(w) > 0);
                  if (first) fillAll(first);
                }}
                sx={{ minHeight: 40 }}
              >
                Copy 1st to all
              </Button>
            </Stack>

            <Box
              sx={{
                maxHeight: { xs: 280, md: 360 },
                overflowY: "auto",
                pr: 0.5,
                WebkitOverflowScrolling: "touch",
              }}
            >
              <Stack spacing={1}>
                {bagWeights.map((weight, index) => (
                  <TextField
                    key={index}
                    fullWidth
                    size="small"
                    label={`Bag ${index + 1} weight (kg)`}
                    type="number"
                    required
                    sx={TOUCH_FIELD_SX}
                    inputProps={{ min: 0, step: 0.001 }}
                    value={weight}
                    disabled={disabled}
                    onChange={(e) => {
                      const next = [...bagWeights];
                      next[index] = e.target.value;
                      onChange(next);
                    }}
                  />
                ))}
              </Stack>
            </Box>

            <Box sx={{ pt: 1, borderTop: 1, borderColor: "divider" }}>
              <Stack spacing={0.25}>
                <SummaryRow label="Bags" value={String(bagWeights.length)} />
                <SummaryRow
                  label="Gross weight (sum of bags)"
                  value={`${grossSum.toLocaleString("en-IN", { maximumFractionDigits: 3 })} kg`}
                  bold
                />
                <SummaryRow
                  label={`Kata (${kataPerBag} kg × ${bagWeights.length} bags)`}
                  value={`−${kataTotal.toLocaleString("en-IN", { maximumFractionDigits: 3 })} kg`}
                />
              </Stack>
            </Box>
          </>
        )}
      </Stack>
    </Card>
  );
}

function SummaryRow({
  label,
  value,
  bold,
}: {
  label: string;
  value: string;
  bold?: boolean;
}) {
  return (
    <Stack direction="row" justifyContent="space-between" alignItems="baseline">
      <Typography variant="body2" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight={bold ? 700 : 500}>
        {value}
      </Typography>
    </Stack>
  );
}
