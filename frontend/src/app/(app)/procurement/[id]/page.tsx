"use client";

import {
  Alert,
  Box,
  Button,
  Card,
  Chip,
  CircularProgress,
  Grid2 as Grid,
  Stack,
  Typography,
} from "@mui/material";
import { ArrowBack } from "@mui/icons-material";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useParams, useSearchParams } from "next/navigation";
import { CommentThread } from "@/components/comments/CommentThread";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { EntityDocumentUpload } from "@/features/documents/entity-document-upload";
import {
  fetchProcurement,
  formatInr,
  STATUS_COLORS,
  STATUS_LABELS,
} from "@/features/procurements/api";
import { resolveProcurementDisplayExtras } from "@/features/procurements/draft-extras";
import { ProcurementWorkflowActions } from "@/features/procurements/workflow-actions";

export default function ProcurementDetailPage() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const procurementDate = searchParams.get("date") ?? new Date().toISOString().slice(0, 10);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["procurement", params.id, procurementDate],
    queryFn: () => fetchProcurement(params.id, procurementDate),
    enabled: Boolean(params.id),
  });

  const display = data
    ? resolveProcurementDisplayExtras(data)
    : {
        buyerName: null,
        paymentTerms: null,
        plannedMoisturePct: null,
        plannedRate: null,
        freeNotes: "",
      };

  return (
    <MuiPageShell
      title={data?.procurement_number ?? "Procurement detail"}
      description={data ? `${data.procurement_date} · ${data.farmer_name ?? "—"}` : "Loading…"}
      actions={
        <Button component={Link} href="/procurement" startIcon={<ArrowBack />} variant="outlined">
          Back to board
        </Button>
      }
    >
      {isLoading && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {isError && (
        <Alert severity="warning">
          {error instanceof Error ? error.message : "Could not load procurement"}
        </Alert>
      )}

      {data && (
        <Stack spacing={2}>
          <Card sx={{ p: 2 }}>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }} flexWrap="wrap" useFlexGap>
              <Chip
                label={STATUS_LABELS[data.status]}
                color={STATUS_COLORS[data.status]}
                size="small"
              />
              {data.tags.map((tag) => (
                <Chip key={tag} label={tag} size="small" variant="outlined" />
              ))}
            </Stack>
            <Grid container spacing={2}>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field label="Farmer" value={data.farmer_name ?? "—"} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field label="Crop" value={data.crop_type_name ?? "—"} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field label="Village" value={data.village_name ?? "—"} />
              </Grid>
              {display.buyerName && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <Field label="Buyer" value={display.buyerName} />
                </Grid>
              )}
              {display.paymentTerms && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <Field label="Payment terms" value={display.paymentTerms} />
                </Grid>
              )}
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field label="Bags" value={String(data.bag_count)} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field label="Gross weight (kg)" value={data.gross_weight_kg} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field
                  label="Per-bag deduction (kg)"
                  value={`${data.per_bag_deduction_kg} × ${data.bag_count} = ${data.bag_weight_deduction_kg} kg`}
                />
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field label="Net weight (kg)" value={data.net_weight_kg} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field
                  label="Moisture %"
                  value={
                    data.moisture_pct != null
                      ? String(data.moisture_pct)
                      : display.plannedMoisturePct
                        ? `${display.plannedMoisturePct} (planned)`
                        : "—"
                  }
                />
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field
                  label="Rate / quintal"
                  value={
                    Number(data.rate_per_quintal) > 0
                      ? formatInr(data.rate_per_quintal)
                      : display.plannedRate
                        ? `${formatInr(display.plannedRate)} (planned)`
                        : "—"
                  }
                />
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field label="Gross amount" value={formatInr(data.gross_amount)} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field label="Deductions" value={formatInr(data.deduction_amount)} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field label="Net amount" value={formatInr(data.net_amount)} />
              </Grid>
              {data.confirmed_by_name && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <Field
                    label="Confirmed by"
                    value={`${data.confirmed_by_name}${data.confirmed_at ? ` · ${data.confirmed_at.slice(0, 10)}` : ""}`}
                  />
                </Grid>
              )}
              {data.cancellation_reason && (
                <Grid size={{ xs: 12 }}>
                  <Field label="Cancellation reason" value={data.cancellation_reason} />
                </Grid>
              )}
              {display.freeNotes && (
                <Grid size={{ xs: 12 }}>
                  <Field label="Notes" value={display.freeNotes} />
                </Grid>
              )}
            </Grid>

            {data.deductions?.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Deduction lines
                </Typography>
                {data.deductions.map((d) => (
                  <Typography key={d.id} variant="body2">
                    {d.deduction_type}: {formatInr(d.amount)}
                    {d.notes ? ` — ${d.notes}` : ""}
                  </Typography>
                ))}
              </Box>
            )}
          </Card>

          <ProcurementWorkflowActions
            procurement={data}
            procurementDate={procurementDate}
            plannedMoisturePct={display.plannedMoisturePct}
          />

          <Card sx={{ p: 2 }}>
            <EntityDocumentUpload entityType="procurement" entityId={data.id} />
          </Card>

          <Card sx={{ p: 2 }}>
            <CommentThread entityType="procurement" entityId={data.id} />
          </Card>
        </Stack>
      )}
    </MuiPageShell>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <Box>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight={500}>
        {value}
      </Typography>
    </Box>
  );
}
