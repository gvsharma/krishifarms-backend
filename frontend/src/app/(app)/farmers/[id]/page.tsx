"use client";

import {
  Alert,
  Box,
  Button,
  Card,
  Chip,
  CircularProgress,
  Grid2 as Grid,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { ArrowBack, EditOutlined } from "@mui/icons-material";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useState } from "react";
import { CommentThread } from "@/components/comments/CommentThread";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import {
  Button as PremiumButton,
  Field as PremiumField,
  Input,
  PREMIUM_SCOPE,
  Scope,
} from "@/components/ui/premium";
import {
  PremiumDialog,
  PremiumDialogActions,
  PremiumDialogContent,
  PremiumDialogTitle,
} from "@/components/ui/premium-dialog";
import { SoftAlert } from "@/components/ui/soft-alert";
import { fetchFarmer, updateFarmer, type FarmerDetail } from "@/features/farmers/api";
import {
  EMPTY_LOCATION_CASCADE,
  LocationCascade,
  type LocationCascadeValue,
} from "@/features/master-data/location-cascade";
import { formatInr } from "@/features/procurements/api";

type EditForm = {
  fullName: string;
  fullNameTe: string;
  phone: string;
  phoneSecondary: string;
  address: string;
  notes: string;
  status: string;
  location: LocationCascadeValue;
};

function formFromFarmer(farmer: FarmerDetail): EditForm {
  return {
    fullName: farmer.full_name,
    fullNameTe: farmer.full_name_te ?? "",
    phone: farmer.phone_primary,
    phoneSecondary: farmer.phone_secondary ?? "",
    address: farmer.address ?? "",
    notes: farmer.notes ?? "",
    status: farmer.status,
    location: {
      ...EMPTY_LOCATION_CASCADE,
      villageId: farmer.village_id,
    },
  };
}

export default function FarmerDetailPage() {
  const params = useParams<{ id: string }>();
  const farmerId = params.id;
  const queryClient = useQueryClient();
  const [editOpen, setEditOpen] = useState(false);
  const [form, setForm] = useState<EditForm | null>(null);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["farmer", farmerId],
    queryFn: () => fetchFarmer(farmerId),
    enabled: Boolean(farmerId),
  });

  const saveMutation = useMutation({
    mutationFn: () => {
      if (!form) throw new Error("No form");
      return updateFarmer(farmerId, {
        full_name: form.fullName.trim(),
        full_name_te: form.fullNameTe.trim() || null,
        phone_primary: form.phone.trim(),
        phone_secondary: form.phoneSecondary.trim() || null,
        address: form.address.trim() || null,
        notes: form.notes.trim() || null,
        status: form.status,
        village_id: form.location.villageId,
      });
    },
    onSuccess: (updated) => {
      queryClient.setQueryData(["farmer", farmerId], updated);
      queryClient.invalidateQueries({ queryKey: ["farmers"] });
      setEditOpen(false);
      setForm(null);
    },
  });

  const openEdit = () => {
    if (!data) return;
    setForm(formFromFarmer(data));
    saveMutation.reset();
    setEditOpen(true);
  };

  const canSave =
    Boolean(form) &&
    form!.fullName.trim().length >= 2 &&
    form!.phone.trim().length >= 10 &&
    Boolean(form!.location.villageId) &&
    !saveMutation.isPending;

  return (
    <MuiPageShell
      title={data?.full_name ?? "Farmer detail"}
      description={data ? `${data.farmer_code} · ${data.village_name ?? "—"}` : "Loading…"}
      actions={
        <Stack direction="row" spacing={1}>
          {data && (
            <Button variant="contained" startIcon={<EditOutlined />} onClick={openEdit}>
              Edit
            </Button>
          )}
          <Button component={Link} href="/farmers" startIcon={<ArrowBack />} variant="outlined">
            Back to list
          </Button>
        </Stack>
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
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Field label="Village" value={data.village_name ?? "—"} />
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

      <PremiumDialog
        open={editOpen && Boolean(form)}
        onClose={() => setEditOpen(false)}
        maxWidth="sm"
      >
        <PremiumDialogTitle>Edit farmer</PremiumDialogTitle>
        <PremiumDialogContent sx={{ overflow: "visible", pt: 0.5, pb: 2 }}>
          {form && (
            <Scope className="flex flex-col gap-5 bg-transparent">
              <PremiumField label="Full name" required>
                <Input
                  autoFocus
                  value={form.fullName}
                  onChange={(e) => setForm({ ...form, fullName: e.target.value })}
                />
              </PremiumField>
              <PremiumField label="Full name (Telugu)">
                <Input
                  value={form.fullNameTe}
                  onChange={(e) => setForm({ ...form, fullNameTe: e.target.value })}
                />
              </PremiumField>
              <PremiumField label="Primary phone" required>
                <Input
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                />
              </PremiumField>
              <PremiumField label="Secondary phone">
                <Input
                  value={form.phoneSecondary}
                  onChange={(e) => setForm({ ...form, phoneSecondary: e.target.value })}
                />
              </PremiumField>

              <LocationCascade
                required
                value={form.location}
                hydrateVillageId={data?.village_id}
                onChange={(location) =>
                  setForm((prev) => (prev ? { ...prev, location } : prev))
                }
              />

              <TextField
                select
                fullWidth
                label="Status"
                value={form.status}
                onChange={(e) => setForm({ ...form, status: e.target.value })}
                sx={{ "& .MuiInputBase-root": { minHeight: 52 } }}
              >
                <MenuItem value="active">active</MenuItem>
                <MenuItem value="inactive">inactive</MenuItem>
                <MenuItem value="blocked">blocked</MenuItem>
              </TextField>

              <PremiumField label="Address">
                <Input
                  value={form.address}
                  onChange={(e) => setForm({ ...form, address: e.target.value })}
                />
              </PremiumField>
              <PremiumField label="Notes">
                <Input
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                />
              </PremiumField>

              {saveMutation.isError && (
                <SoftAlert severity="error">
                  {saveMutation.error instanceof Error
                    ? saveMutation.error.message
                    : "Save failed"}
                </SoftAlert>
              )}
            </Scope>
          )}
        </PremiumDialogContent>
        <PremiumDialogActions className={PREMIUM_SCOPE}>
          <PremiumButton variant="secondary" size="sm" onClick={() => setEditOpen(false)}>
            Cancel
          </PremiumButton>
          <PremiumButton
            variant="primary"
            size="sm"
            disabled={!canSave}
            onClick={() => saveMutation.mutate()}
          >
            {saveMutation.isPending ? "Saving…" : "Save"}
          </PremiumButton>
        </PremiumDialogActions>
      </PremiumDialog>
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
