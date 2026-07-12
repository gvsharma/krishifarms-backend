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
import {
  fetchProcurement,
  formatInr,
  STATUS_LABELS,
} from "@/features/procurements/api";

export default function ProcurementDetailPage() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const procurementDate = searchParams.get("date") ?? new Date().toISOString().slice(0, 10);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["procurement", params.id, procurementDate],
    queryFn: () => fetchProcurement(params.id, procurementDate),
    enabled: Boolean(params.id),
  });

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
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
              <Chip label={STATUS_LABELS[data.status]} color="primary" size="small" />
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
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field label="Bags" value={String(data.bag_count)} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field label="Gross weight (kg)" value={data.gross_weight_kg} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field label="Net weight (kg)" value={data.net_weight_kg} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field label="Rate / quintal" value={formatInr(data.rate_per_quintal)} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4 }}>
                <Field label="Net amount" value={formatInr(data.net_amount)} />
              </Grid>
              {data.notes && (
                <Grid size={{ xs: 12 }}>
                  <Field label="Notes" value={data.notes} />
                </Grid>
              )}
            </Grid>
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
