"use client";

import {
  Box,
  Button,
  Card,
  Chip,
  CircularProgress,
  FormControlLabel,
  IconButton,
  MenuItem,
  Stack,
  Switch,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { Add, EditOutlined } from "@mui/icons-material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import {
  PremiumDialog,
  PremiumDialogActions,
  PremiumDialogContent,
  PremiumDialogTitle,
} from "@/components/ui/premium-dialog";
import { SoftAlert } from "@/components/ui/soft-alert";
import { useAuth } from "@/hooks/use-auth";
import { createUser, fetchRoles, fetchUsers, updateUser, type User } from "@/features/settings/api";

type FormState = {
  full_name: string;
  email: string;
  phone: string;
  password: string;
  role_id: string;
  preferred_locale: string;
  is_active: boolean;
};

const emptyForm = (): FormState => ({
  full_name: "",
  email: "",
  phone: "",
  password: "",
  role_id: "",
  preferred_locale: "en",
  is_active: true,
});

export default function SettingsUsersPage() {
  const queryClient = useQueryClient();
  const { canManageUsers } = useAuth();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<User | null>(null);
  const [form, setForm] = useState<FormState>(emptyForm);

  const usersQuery = useQuery({ queryKey: ["users"], queryFn: () => fetchUsers() });
  const rolesQuery = useQuery({ queryKey: ["roles"], queryFn: fetchRoles });

  const phoneDigits = form.phone.replace(/\D/g, "");
  const phoneValid = phoneDigits.length >= 10;

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (!phoneValid) {
        throw new Error("Phone is required (at least 10 digits)");
      }
      const phone = phoneDigits;
      if (editing) {
        return updateUser(editing.id, {
          full_name: form.full_name.trim(),
          phone,
          role_id: form.role_id,
          preferred_locale: form.preferred_locale,
          is_active: form.is_active,
          ...(form.password.trim() ? { password: form.password.trim() } : {}),
        });
      }
      return createUser({
        full_name: form.full_name.trim(),
        role_id: form.role_id,
        email: form.email.trim() || null,
        phone,
        password: form.password.trim() || null,
        preferred_locale: form.preferred_locale,
      });
    },
    onSuccess: () => {
      setDialogOpen(false);
      setEditing(null);
      setForm(emptyForm());
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm());
    saveMutation.reset();
    setDialogOpen(true);
  };

  const openEdit = (user: User) => {
    setEditing(user);
    setForm({
      full_name: user.full_name,
      email: user.email ?? "",
      phone: user.phone ?? "",
      password: "",
      role_id: user.role.id,
      preferred_locale: user.preferred_locale || "en",
      is_active: user.is_active,
    });
    saveMutation.reset();
    setDialogOpen(true);
  };

  const canSave =
    form.full_name.trim().length >= 2 &&
    form.role_id &&
    phoneValid &&
    (editing ? true : !form.email.trim() || form.password.trim().length >= 8);

  return (
    <MuiPageShell
      title="Users"
      description="Organization members, roles, and access. Requires users:read permission."
      actions={
        canManageUsers ? (
          <Button variant="contained" startIcon={<Add />} onClick={openCreate}>
            Add user
          </Button>
        ) : undefined
      }
    >
      <Card sx={{ overflow: "hidden" }}>
        {usersQuery.isLoading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
            <CircularProgress />
          </Box>
        )}

        {usersQuery.isError && (
          <SoftAlert severity="warning" sx={{ m: 2 }}>
            {usersQuery.error instanceof Error
              ? usersQuery.error.message
              : "Could not load users. Sign in or check API connectivity."}
          </SoftAlert>
        )}

        {!usersQuery.isLoading && usersQuery.data && (
          <>
            <Box sx={{ px: 2, py: 1.5, borderBottom: 1, borderColor: "divider" }}>
              <Typography variant="body2" color="text.secondary">
                {usersQuery.data.total} user{usersQuery.data.total === 1 ? "" : "s"}
              </Typography>
            </Box>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Email / Phone</TableCell>
                    <TableCell>Role</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Last login</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {usersQuery.data.items.map((user) => (
                    <TableRow key={user.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight={500}>
                          {user.full_name}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{user.email ?? user.phone ?? "—"}</Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={user.role.name} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={user.is_active ? "Active" : "Inactive"}
                          size="small"
                          color={user.is_active ? "success" : "default"}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" color="text.secondary">
                          {user.last_login_at
                            ? new Date(user.last_login_at).toLocaleDateString("en-IN")
                            : "Never"}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <IconButton size="small" aria-label="Edit user" onClick={() => openEdit(user)}>
                          <EditOutlined fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                  {usersQuery.data.items.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                          No users found
                        </Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </>
        )}
      </Card>

      <PremiumDialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm">
        <PremiumDialogTitle>{editing ? "Edit user" : "Add user"}</PremiumDialogTitle>
        <PremiumDialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <TextField
              autoFocus
              label="Full name"
              fullWidth
              required
              value={form.full_name}
              onChange={(e) => setForm((p) => ({ ...p, full_name: e.target.value }))}
            />
            {!editing && (
              <TextField
                label="Email"
                fullWidth
                type="email"
                value={form.email}
                onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
                helperText="Required with password for web login; leave empty for phone-only field staff"
              />
            )}
            <TextField
              label="Phone"
              fullWidth
              required
              value={form.phone}
              onChange={(e) => setForm((p) => ({ ...p, phone: e.target.value }))}
              error={form.phone.length > 0 && !phoneValid}
              helperText="Required for staff (10+ digits). Used for phone login and future OTP."
            />
            <TextField
              label={editing ? "New password (optional)" : "Password"}
              fullWidth
              type="password"
              value={form.password}
              onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
              helperText={!editing ? "Required when email is set (min 8 chars)" : undefined}
            />
            <TextField
              select
              label="Role"
              fullWidth
              required
              value={form.role_id}
              onChange={(e) => setForm((p) => ({ ...p, role_id: e.target.value }))}
            >
              {(rolesQuery.data ?? []).map((role) => (
                <MenuItem key={role.id} value={role.id}>
                  {role.name} ({role.code})
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              label="Locale"
              fullWidth
              value={form.preferred_locale}
              onChange={(e) => setForm((p) => ({ ...p, preferred_locale: e.target.value }))}
            >
              <MenuItem value="en">English</MenuItem>
              <MenuItem value="te">Telugu</MenuItem>
            </TextField>
            {editing && (
              <FormControlLabel
                control={
                  <Switch
                    checked={form.is_active}
                    onChange={(e) => setForm((p) => ({ ...p, is_active: e.target.checked }))}
                  />
                }
                label="Active"
              />
            )}
            {saveMutation.isError && (
              <SoftAlert severity="error">
                {saveMutation.error instanceof Error ? saveMutation.error.message : "Save failed"}
              </SoftAlert>
            )}
          </Stack>
        </PremiumDialogContent>
        <PremiumDialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            disabled={!canSave || saveMutation.isPending}
            onClick={() => saveMutation.mutate()}
          >
            {saveMutation.isPending ? "Saving…" : "Save"}
          </Button>
        </PremiumDialogActions>
      </PremiumDialog>
    </MuiPageShell>
  );
}
