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
import { useTranslations } from "@/i18n/use-translations";

export default function FarmerDetailPage() {
  const { t } = useTranslations();
  const params = useParams<{ id: string }>();
  const farmerId = params.id;

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["farmer", farmerId],
    queryFn: () => fetchFarmer(farmerId),
    enabled: Boolean(farmerId),
  });

  return (
    <MuiPageShell
      title={data?.full_name ?? t("operations.farmers.detail.title")}
      description={
        data
          ? `${data.farmer_code} · ${data.village_name ?? t("common.dash")}`
          : t("common.loading")
      }
      actions={
        <Button component={Link} href="/farmers" startIcon={<ArrowBack />} variant="outlined">
          {t("common.backToList")}
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
          {error instanceof Error ? error.message : t("operations.farmers.detail.loadError")}
        </Alert>
      )}

      {data && (
        <Stack spacing={2}>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 8 }}>
              <Card sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                  {t("operations.farmers.detail.profile")}
                </Typography>
                <Grid container spacing={1}>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Field label={t("operations.farmers.detail.phone")} value={data.phone_primary} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Field
                      label={t("operations.farmers.detail.secondary")}
                      value={data.phone_secondary ?? t("common.dash")}
                    />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Field label={t("common.status")} value={data.status} />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <Field label={t("operations.farmers.detail.address")} value={data.address ?? t("common.dash")} />
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
                  {t("operations.farmers.detail.outstanding")}
                </Typography>
                <Typography variant="h4" color="primary.main" fontWeight={700}>
                  {formatInr(data.outstanding_amount ?? "0")}
                </Typography>
              </Card>
            </Grid>
          </Grid>

          <Card sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              {t("operations.farmers.detail.bankAccounts")}
            </Typography>
            {data.bank_accounts.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                {t("operations.farmers.detail.noBankAccounts")}
              </Typography>
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>{t("operations.farmers.detail.holder")}</TableCell>
                    <TableCell>{t("operations.farmers.detail.bank")}</TableCell>
                    <TableCell>{t("operations.farmers.detail.ifsc")}</TableCell>
                    <TableCell>{t("operations.farmers.detail.account")}</TableCell>
                    <TableCell>{t("operations.farmers.detail.primary")}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data.bank_accounts.map((account) => (
                    <TableRow key={account.id}>
                      <TableCell>{account.account_holder_name}</TableCell>
                      <TableCell>{account.bank_name}</TableCell>
                      <TableCell>{account.ifsc}</TableCell>
                      <TableCell>{account.account_number_masked}</TableCell>
                      <TableCell>{account.is_primary ? t("common.yes") : t("common.dash")}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </Card>

          <Card sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              {t("operations.farmers.detail.landParcels")}
            </Typography>
            {data.land_parcels.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                {t("operations.farmers.detail.noLandParcels")}
              </Typography>
            ) : (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>{t("operations.farmers.detail.surveyNumber")}</TableCell>
                    <TableCell>{t("operations.farmers.detail.acres")}</TableCell>
                    <TableCell>{t("common.type")}</TableCell>
                    <TableCell>{t("operations.farmers.detail.gps")}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data.land_parcels.map((parcel) => (
                    <TableRow key={parcel.id}>
                      <TableCell>{parcel.survey_number}</TableCell>
                      <TableCell>{parcel.acres}</TableCell>
                      <TableCell>{parcel.land_type ?? t("common.dash")}</TableCell>
                      <TableCell>
                        {parcel.geo_lat && parcel.geo_lng
                          ? `${parcel.geo_lat}, ${parcel.geo_lng}`
                          : t("common.dash")}
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
