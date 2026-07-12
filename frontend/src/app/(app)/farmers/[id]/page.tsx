"use client";

import {
  Alert,
  Box,
  Button,
  Card,
  Chip,
  CircularProgress,
  Divider,
  Grid2 as Grid,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { ArrowBack } from "@mui/icons-material";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { CommentThread } from "@/components/comments/CommentThread";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { fetchFarmer } from "@/features/farmers/api";
import { formatInr } from "@/features/procurements/api";

export default function FarmerDetailPage() {
  const params = useParams<{ id: string }>();
  const farmerId = params.id;

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["farmer", farmerId],
    queryFn: () => fetchFarmer(farmerId),
    enabled: Boolean(farmerId),
  });

  return (
    <MuiPageShell
      title={data?.full_name ?? "Farmer detail"}
      description={data ? `${data.farmer_code} · ${data.village_name ?? "—"}` : "Loading…"}
      actions={
        <Button component={Link} href="/farmers" startIcon={<ArrowBack />} variant="outlined">
          Back to list
        </Button>
      }
    >
      {isLoading && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {isError && (
        <Alert severity="warning">{error instanceof Error ? error.message : "Could not load farmer"}</Alert>
      )}

      {data && (
        <Stack spacing={2}>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 8 }}>
              <Card sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Profile
                </Typography>
                <Grid container spacing={1}>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Field label="Phone" value={data.phone_primary} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Field label="Secondary" value={data.phone_secondary ?? "—"} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Field label="Status" value={data.status} />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <Field label="Address" value={data.address ?? "—"} />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <Stack direction="row" spacing={1} flexWrap="wrap">
                      {data.tags.map((tag) => (
                        <Chip key={tag} label={tag} size="small" />
                      ))}
                    </Stack>
                  </Grid>
                </Grid>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, md: 4 }}>
              <Card sx={{ p: 2 }}>
                <Typography variant="overline" color="text.secondary">
                  Outstanding
                </Typography>
                <Typography variant="h4" color="primary.main" fontWeight={700}>
                  {formatInr(data.outstanding_amount ?? "0")}
                </Typography>
              </Card>
            </Grid>
          </Grid>

          <Card sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Bank accounts
            </Typography>
            {data.bank_accounts.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No bank accounts on file
              </Typography>
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Holder</TableCell>
                    <TableCell>Bank</TableCell>
                    <TableCell>IFSC</TableCell>
                    <TableCell>Account</TableCell>
                    <TableCell>Primary</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data.bank_accounts.map((account) => (
                    <TableRow key={account.id}>
                      <TableCell>{account.account_holder_name}</TableCell>
                      <TableCell>{account.bank_name}</TableCell>
                      <TableCell>{account.ifsc}</TableCell>
                      <TableCell>{account.account_number_masked}</TableCell>
                      <TableCell>{account.is_primary ? "Yes" : "—"}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </Card>

          <Card sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Land parcels
            </Typography>
            {data.land_parcels.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No land parcels recorded
              </Typography>
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Survey #</TableCell>
                    <TableCell>Acres</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>GPS</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data.land_parcels.map((parcel) => (
                    <TableRow key={parcel.id}>
                      <TableCell>{parcel.survey_number}</TableCell>
                      <TableCell>{parcel.acres}</TableCell>
                      <TableCell>{parcel.land_type ?? "—"}</TableCell>
                      <TableCell>
                        {parcel.geo_lat && parcel.geo_lng
                          ? `${parcel.geo_lat}, ${parcel.geo_lng}`
                          : "—"}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </Card>

          <Card sx={{ p: 2 }}>
            <CommentThread entityType="farmer" entityId={data.id} />
          </Card>
        </Stack>
      )}
    </MuiPageShell>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <Box sx={{ mb: 1.5 }}>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2">{value}</Typography>
    </Box>
  );
}
