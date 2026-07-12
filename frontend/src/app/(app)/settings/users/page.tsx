"use client";

import {
  Alert,
  Box,
  Button,
  Card,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  FormControlLabel,
  IconButton,
  MenuItem,
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
import { useAuth } from "@/hooks/use-auth";
import { createUser, fetchRoles, fetchUsers, updateUser, type User } from "@/features/settings/api";
import { useTranslations } from "@/i18n/use-translations";

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
  const { t } = useTranslations();
  const queryClient = useQueryClient();
  const { canManageUsers } = useAuth();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<User | null>(null);
  const [form, setForm] = useState<FormState>(emptyForm);

  const usersQuery = useQuery({ queryKey: ["users"], queryFn: () => fetchUsers() });
  const rolesQuery = useQuery({ queryKey: ["roles"], queryFn: fetchRoles });

  const saveMutation = useMutation({
    mutationFn: async () => {
      if (editing) {
        return updateUser(editing.id, {
          full_name: form.full_name.trim(),
          phone: form.phone.trim() || null,
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
        phone: form.phone.trim() || null,
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
    setDialogOpen(true);
  };

  const canSave =
    form.full_name.trim().length >= 2 &&
    form.role_id &&
    (editing
      ? true
      : Boolean(form.email.trim() || form.phone.trim()) &&
        (!form.email.trim() || form.password.trim().length >= 8));

  const userCountLabel =
    usersQuery.data?.total === 1
      ? t("settings.usersPage.userCountOne", { count: usersQuery.data.total })
      : t("settings.usersPage.userCount", { count: usersQuery.data?.total ?? 0 });

  return (
    <MuiPageShell
      title={t("settings.usersPage.title")}
      description={t("settings.usersPage.description")}
      actions={
        canManageUsers ? (
          <Button variant="contained" startIcon={<Add />} onClick={openCreate}>
            {t("settings.usersPage.addUser")}
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
          <Alert severity="warning" sx={{ m: 2 }}>
            {usersQuery.error instanceof Error
              ? usersQuery.error.message
              : t("errors.usersLoadFailed")}
          </Alert>
        )}

        {!usersQuery.isLoading && usersQuery.data && (
          <>
            <Box sx={{ px: 2, py: 1.5, borderBottom: 1, borderColor: "divider" }}>
              <Typography variant="body2" color="text.secondary">
                {userCountLabel}
              </Typography>
            </Box>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>{t("common.name")}</TableCell>
                    <TableCell>{t("settings.usersPage.emailPhone")}</TableCell>
                    <TableCell>{t("common.role")}</TableCell>
                    <TableCell>{t("common.status")}</TableCell>
                    <TableCell>{t("settings.usersPage.lastLogin")}</TableCell>
                    <TableCell align="right">{t("common.actions")}</TableCell>
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
                        <Typography variant="body2">{user.email ?? user.phone ?? t("common.dash")}</Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={user.role.name} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={user.is_active ? t("common.active") : t("common.inactive")}
                          size="small"
                          color={user.is_active ? "success" : "default"}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="caption" color="text.secondary">
                          {user.last_login_at
                            ? new Date(user.last_login_at).toLocaleDateString("en-IN")
                            : t("common.never")}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <IconButton
                          size="small"
                          aria-label={t("dialog.editUserAria")}
                          onClick={() => openEdit(user)}
                        >
                          <EditOutlined fontSize="small" />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                  {usersQuery.data.items.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                          {t("settings.usersPage.noUsers")}
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

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editing ? t("dialog.editUser") : t("dialog.addUser")}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label={t("settings.usersPage.fullName")}
            fullWidth
            required
            value={form.full_name}
            onChange={(e) => setForm((p) => ({ ...p, full_name: e.target.value }))}
          />
          {!editing && (
            <TextField
              margin="dense"
              label={t("common.email")}
              fullWidth
              type="email"
              value={form.email}
              onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
              helperText={t("settings.usersPage.emailHelper")}
            />
          )}
          <TextField
            margin="dense"
            label={t("common.phone")}
            fullWidth
            value={form.phone}
            onChange={(e) => setForm((p) => ({ ...p, phone: e.target.value }))}
          />
          <TextField
            margin="dense"
            label={editing ? t("settings.usersPage.newPassword") : t("common.password")}
            fullWidth
            type="password"
            value={form.password}
            onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
            helperText={!editing ? t("settings.usersPage.passwordHelper") : undefined}
          />
          <TextField
            select
            margin="dense"
            label={t("common.role")}
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
            margin="dense"
            label={t("common.locale")}
            fullWidth
            value={form.preferred_locale}
            onChange={(e) => setForm((p) => ({ ...p, preferred_locale: e.target.value }))}
          >
            <MenuItem value="en">{t("profile.english")}</MenuItem>
            <MenuItem value="te">{t("profile.telugu")}</MenuItem>
          </TextField>
          {editing && (
            <FormControlLabel
              sx={{ mt: 1 }}
              control={
                <Switch
                  checked={form.is_active}
                  onChange={(e) => setForm((p) => ({ ...p, is_active: e.target.checked }))}
                />
              }
              label={t("common.active")}
            />
          )}
          {saveMutation.isError && (
            <Alert severity="error" sx={{ mt: 1 }}>
              {saveMutation.error instanceof Error ? saveMutation.error.message : t("errors.saveFailed")}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>{t("common.cancel")}</Button>
          <Button
            variant="contained"
            disabled={!canSave || saveMutation.isPending}
            onClick={() => saveMutation.mutate()}
          >
            {saveMutation.isPending ? t("common.saving") : t("common.save")}
          </Button>
        </DialogActions>
      </Dialog>
    </MuiPageShell>
  );
}
