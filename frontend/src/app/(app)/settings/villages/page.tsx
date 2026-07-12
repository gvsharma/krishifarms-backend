"use client";

import {
  Box,
  Button,
  Card,
  CircularProgress,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { Add, DeleteOutline, EditOutlined } from "@mui/icons-material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import {
  Button as PremiumButton,
  Field,
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
import { useAuth } from "@/hooks/use-auth";
import {
  createVillage,
  deleteVillage,
  fetchVillages,
  updateVillage,
  type Village,
} from "@/features/master-data/api";
import {
  EMPTY_LOCATION_CASCADE,
  LocationCascade,
  type LocationCascadeValue,
} from "@/features/master-data/location-cascade";

type FormState = {
  name: string;
  state: string;
  pincode: string;
  location: LocationCascadeValue;
};

const emptyForm = (): FormState => ({
  name: "",
  state: "Telangana",
  pincode: "",
  location: { ...EMPTY_LOCATION_CASCADE },
});

export default function SettingsVillagesPage() {
  const queryClient = useQueryClient();
  const { canDelete } = useAuth();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Village | null>(null);
  const [form, setForm] = useState<FormState>(emptyForm);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["villages"],
    queryFn: () => fetchVillages(1, 200),
  });

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        name: form.name.trim(),
        district_id: form.location.districtId || null,
        mandal_id: form.location.mandalId || null,
        state: form.state.trim() || null,
        pincode: form.pincode.trim() || null,
      };
      if (editing) return updateVillage(editing.id, payload);
      return createVillage(payload);
    },
    onSuccess: () => {
      setDialogOpen(false);
      setEditing(null);
      setForm(emptyForm());
      queryClient.invalidateQueries({ queryKey: ["villages"] });
      queryClient.invalidateQueries({ queryKey: ["villages", "cascade"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteVillage(id),
    onSuccess: () => {
      setDeleteId(null);
      queryClient.invalidateQueries({ queryKey: ["villages"] });
      queryClient.invalidateQueries({ queryKey: ["villages", "cascade"] });
    },
  });

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm());
    saveMutation.reset();
    setDialogOpen(true);
  };

  const openEdit = (row: Village) => {
    setEditing(row);
    setForm({
      name: row.name,
      state: row.state ?? "",
      pincode: row.pincode ?? "",
      location: {
        districtId: row.district_id ?? "",
        mandalId: row.mandal_id ?? "",
        villageId: "",
      },
    });
    saveMutation.reset();
    setDialogOpen(true);
  };

  const canSave =
    form.name.trim().length >= 2 &&
    Boolean(form.location.districtId) &&
    Boolean(form.location.mandalId) &&
    !saveMutation.isPending;

  return (
    <MuiPageShell
      title="Villages"
      description="Geography master for farmers, agents, and procurements. Pick District → Mandal from location masters."
      actions={
        <Button variant="contained" startIcon={<Add />} onClick={openCreate}>
          Add
        </Button>
      }
    >
      <Card sx={{ overflow: "hidden" }}>
        {isLoading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
            <CircularProgress />
          </Box>
        )}

        {isError && (
          <SoftAlert severity="warning" sx={{ m: 2 }}>
            {error instanceof Error ? error.message : "Could not load villages"}
          </SoftAlert>
        )}

        {!isLoading && data && (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Mandal</TableCell>
                  <TableCell>District</TableCell>
                  <TableCell>State</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.items.map((row) => (
                  <TableRow key={row.id} hover>
                    <TableCell>{row.name}</TableCell>
                    <TableCell>{row.mandal ?? "—"}</TableCell>
                    <TableCell>{row.district ?? "—"}</TableCell>
                    <TableCell>{row.state ?? "—"}</TableCell>
                    <TableCell align="right">
                      <IconButton size="small" aria-label="Edit" onClick={() => openEdit(row)}>
                        <EditOutlined fontSize="small" />
                      </IconButton>
                      {canDelete && (
                        <IconButton
                          size="small"
                          aria-label="Delete"
                          color="error"
                          onClick={() => setDeleteId(row.id)}
                        >
                          <DeleteOutline fontSize="small" />
                        </IconButton>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
                {data.items.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                        No records yet — seed Rangareddy with{" "}
                        <code>python -m scripts.seed_locations</code>
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Card>

      <PremiumDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="sm"
        data-testid="catalog-admin-dialog"
      >
        <PremiumDialogTitle>{editing ? "Edit Village" : "Add Village"}</PremiumDialogTitle>
        <PremiumDialogContent sx={{ overflow: "visible", pt: 0.5, pb: 2 }}>
          <Scope className="flex flex-col gap-5 bg-transparent">
            <Field label="Name" required>
              <Input
                autoFocus
                required
                value={form.name}
                onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
              />
            </Field>

            <LocationCascade
              showVillage={false}
              required
              value={form.location}
              onChange={(location) => setForm((prev) => ({ ...prev, location }))}
            />

            <Field label="State">
              <Input
                value={form.state}
                onChange={(e) => setForm((prev) => ({ ...prev, state: e.target.value }))}
              />
            </Field>

            <Field label="Pincode">
              <Input
                value={form.pincode}
                onChange={(e) => setForm((prev) => ({ ...prev, pincode: e.target.value }))}
              />
            </Field>

            {saveMutation.isError && (
              <SoftAlert severity="error">
                {saveMutation.error instanceof Error ? saveMutation.error.message : "Save failed"}
              </SoftAlert>
            )}
          </Scope>
        </PremiumDialogContent>
        <PremiumDialogActions className={PREMIUM_SCOPE}>
          <PremiumButton variant="secondary" size="sm" onClick={() => setDialogOpen(false)}>
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

      <PremiumDialog
        open={Boolean(deleteId) && canDelete}
        onClose={() => {
          setDeleteId(null);
          deleteMutation.reset();
        }}
        maxWidth="xs"
      >
        <PremiumDialogTitle>Delete record?</PremiumDialogTitle>
        <PremiumDialogContent>
          <Typography variant="body2" sx={{ color: "text.secondary" }}>
            {(() => {
              const row = data?.items.find((r) => r.id === deleteId);
              return row
                ? `Soft-delete ${row.name}?`
                : "This soft-deletes the record. It will no longer appear in lists.";
            })()}
          </Typography>
          {deleteMutation.isError && (
            <SoftAlert severity="error" sx={{ mt: 1.5 }}>
              {deleteMutation.error instanceof Error
                ? deleteMutation.error.message
                : "Delete failed"}
            </SoftAlert>
          )}
        </PremiumDialogContent>
        <PremiumDialogActions className={PREMIUM_SCOPE}>
          <PremiumButton
            variant="secondary"
            size="sm"
            onClick={() => {
              setDeleteId(null);
              deleteMutation.reset();
            }}
          >
            Cancel
          </PremiumButton>
          <PremiumButton
            variant="danger"
            size="sm"
            disabled={!deleteId || deleteMutation.isPending}
            onClick={() => deleteId && deleteMutation.mutate(deleteId)}
          >
            {deleteMutation.isPending ? "Deleting…" : "Delete"}
          </PremiumButton>
        </PremiumDialogActions>
      </PremiumDialog>
    </MuiPageShell>
  );
}
