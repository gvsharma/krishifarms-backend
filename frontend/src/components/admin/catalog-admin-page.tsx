"use client";

import {
  Box,
  Button,
  Card,
  CircularProgress,
  FormControlLabel,
  IconButton,
  Switch,
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
import { useMemo, useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import {
  Button as PremiumButton,
  Field,
  Input,
  PREMIUM_SCOPE,
  Scope,
  Textarea,
} from "@/components/ui/premium";
import { controlBase, controlHeight, controlPadding } from "@/components/ui/premium/styles";
import {
  PremiumDialog,
  PremiumDialogActions,
  PremiumDialogContent,
  PremiumDialogTitle,
} from "@/components/ui/premium-dialog";
import { SoftAlert } from "@/components/ui/soft-alert";
import { useAuth } from "@/hooks/use-auth";
import { cn } from "@/lib/utils";

export type CatalogFieldType = "text" | "number" | "boolean" | "select" | "date";

export interface CatalogField {
  key: string;
  label: string;
  type?: CatalogFieldType;
  required?: boolean;
  createOnly?: boolean;
  /** Show in table (default true). */
  table?: boolean;
  options?: { value: string; label: string }[];
  placeholder?: string;
}

export interface CatalogAdminPageProps<T extends { id: string }> {
  title: string;
  description: string;
  queryKey: string;
  fields: CatalogField[];
  list: () => Promise<{ items: T[]; total: number }>;
  create: (payload: Record<string, unknown>) => Promise<T>;
  update: (id: string, payload: Record<string, unknown>) => Promise<T>;
  remove?: (id: string) => Promise<unknown>;
  /** Optional row label renderer for confirm dialogs. */
  rowLabel?: (row: T) => string;
  /** Map row → form values for edit. */
  toFormValues?: (row: T) => Record<string, string | boolean>;
  /** Transform form values before API call. */
  toPayload?: (values: Record<string, string | boolean>, mode: "create" | "edit") => Record<string, unknown>;
}

function defaultForm(fields: CatalogField[]): Record<string, string | boolean> {
  const values: Record<string, string | boolean> = {};
  for (const field of fields) {
    values[field.key] = field.type === "boolean" ? true : "";
  }
  return values;
}

function defaultToFormValues<T extends { id: string }>(
  row: T,
  fields: CatalogField[],
): Record<string, string | boolean> {
  const values = defaultForm(fields);
  for (const field of fields) {
    const raw = (row as Record<string, unknown>)[field.key];
    if (field.type === "boolean") {
      values[field.key] = Boolean(raw ?? true);
    } else if (raw == null) {
      values[field.key] = "";
    } else {
      values[field.key] = String(raw);
    }
  }
  return values;
}

function defaultToPayload(
  values: Record<string, string | boolean>,
  fields: CatalogField[],
  mode: "create" | "edit",
): Record<string, unknown> {
  const payload: Record<string, unknown> = {};
  for (const field of fields) {
    if (mode === "edit" && field.createOnly) continue;
    const raw = values[field.key];
    if (field.type === "boolean") {
      payload[field.key] = Boolean(raw);
      continue;
    }
    if (typeof raw !== "string") continue;
    const trimmed = raw.trim();
    if (!trimmed) {
      if (field.required && mode === "create") payload[field.key] = trimmed;
      else if (!field.required) payload[field.key] = null;
      continue;
    }
    if (field.type === "number") {
      payload[field.key] = Number(trimmed);
    } else {
      payload[field.key] = trimmed;
    }
  }
  return payload;
}

/** Plural page titles → singular dialog entity label. */
function singularEntity(title: string): string {
  if (/ies$/i.test(title)) return title.replace(/ies$/i, "y");
  if (/s$/i.test(title)) return title.replace(/s$/i, "");
  return title;
}

const MULTILINE_KEYS = /^(notes|address|description)$/i;

export function CatalogAdminPage<T extends { id: string }>({
  title,
  description,
  queryKey,
  fields,
  list,
  create,
  update,
  remove,
  rowLabel,
  toFormValues,
  toPayload,
}: CatalogAdminPageProps<T>) {
  const queryClient = useQueryClient();
  const { canDelete } = useAuth();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<T | null>(null);
  const [form, setForm] = useState<Record<string, string | boolean>>(() => defaultForm(fields));
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const tableFields = useMemo(() => fields.filter((f) => f.table !== false), [fields]);
  const dialogFields = useMemo(
    () => fields.filter((f) => !(editing && f.createOnly)),
    [fields, editing],
  );
  const entityLabel = useMemo(() => singularEntity(title), [title]);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: [queryKey],
    queryFn: list,
  });

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = toPayload
        ? toPayload(form, editing ? "edit" : "create")
        : defaultToPayload(form, fields, editing ? "edit" : "create");
      if (editing) return update(editing.id, payload);
      return create(payload);
    },
    onSuccess: () => {
      setDialogOpen(false);
      setEditing(null);
      setForm(defaultForm(fields));
      queryClient.invalidateQueries({ queryKey: [queryKey] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => {
      if (!remove) throw new Error("Delete not supported");
      return remove(id);
    },
    onSuccess: () => {
      setDeleteId(null);
      queryClient.invalidateQueries({ queryKey: [queryKey] });
    },
  });

  const showDelete = Boolean(remove) && canDelete;

  const openCreate = () => {
    setEditing(null);
    setForm(defaultForm(fields));
    saveMutation.reset();
    setDialogOpen(true);
  };

  const openEdit = (row: T) => {
    setEditing(row);
    setForm(toFormValues ? toFormValues(row) : defaultToFormValues(row, fields));
    saveMutation.reset();
    setDialogOpen(true);
  };

  const canSave = dialogFields
    .filter((f) => f.required)
    .every((f) => {
      const v = form[f.key];
      if (f.type === "boolean") return true;
      return typeof v === "string" && v.trim().length > 0;
    });

  const firstFocusable = dialogFields.find((f) => f.type !== "boolean");

  return (
    <MuiPageShell
      title={title}
      description={description}
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
            {error instanceof Error ? error.message : `Could not load ${title.toLowerCase()}`}
          </SoftAlert>
        )}

        {!isLoading && data && (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  {tableFields.map((f) => (
                    <TableCell key={f.key}>{f.label}</TableCell>
                  ))}
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.items.map((row) => (
                  <TableRow key={row.id} hover>
                    {tableFields.map((f) => {
                      const raw = (row as unknown as Record<string, unknown>)[f.key];
                      let display = "—";
                      if (f.type === "boolean") display = raw ? "Active" : "Inactive";
                      else if (raw != null && raw !== "") display = String(raw);
                      return <TableCell key={f.key}>{display}</TableCell>;
                    })}
                    <TableCell align="right">
                      <IconButton size="small" aria-label="Edit" onClick={() => openEdit(row)}>
                        <EditOutlined fontSize="small" />
                      </IconButton>
                      {showDelete && (
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
                    <TableCell colSpan={tableFields.length + 1} align="center">
                      <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                        No records yet
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
        <PremiumDialogTitle>
          {editing ? `Edit ${entityLabel}` : `Add ${entityLabel}`}
        </PremiumDialogTitle>
        <PremiumDialogContent sx={{ overflow: "visible", pt: 0.5, pb: 2 }}>
          <Scope className="flex flex-col gap-5 bg-transparent">
            {dialogFields.map((field) => {
              if (field.type === "boolean") {
                return (
                  <FormControlLabel
                    key={field.key}
                    sx={{ display: "block", ml: 0, mr: 0 }}
                    control={
                      <Switch
                        checked={Boolean(form[field.key])}
                        onChange={(e) =>
                          setForm((prev) => ({ ...prev, [field.key]: e.target.checked }))
                        }
                      />
                    }
                    label={field.label}
                  />
                );
              }

              if (field.type === "select" && field.options) {
                return (
                  <Field key={field.key} label={field.label} required={field.required}>
                    <select
                      className={cn(controlBase, controlHeight, controlPadding, "pr-10")}
                      required={field.required}
                      value={String(form[field.key] ?? "")}
                      onChange={(e) =>
                        setForm((prev) => ({ ...prev, [field.key]: e.target.value }))
                      }
                      autoFocus={field === firstFocusable}
                      style={{
                        backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%236B7280' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E")`,
                        backgroundRepeat: "no-repeat",
                        backgroundPosition: "right 14px center",
                      }}
                    >
                      {!field.required && <option value="">—</option>}
                      {field.options.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </Field>
                );
              }

              if (MULTILINE_KEYS.test(field.key)) {
                return (
                  <Field key={field.key} label={field.label} required={field.required}>
                    <Textarea
                      autoFocus={field === firstFocusable}
                      required={field.required}
                      placeholder={field.placeholder}
                      rows={3}
                      value={String(form[field.key] ?? "")}
                      onChange={(e) =>
                        setForm((prev) => ({ ...prev, [field.key]: e.target.value }))
                      }
                    />
                  </Field>
                );
              }

              return (
                <Field key={field.key} label={field.label} required={field.required}>
                  <Input
                    autoFocus={field === firstFocusable}
                    required={field.required}
                    type={
                      field.type === "number" ? "number" : field.type === "date" ? "date" : "text"
                    }
                    placeholder={field.placeholder}
                    value={String(form[field.key] ?? "")}
                    onChange={(e) =>
                      setForm((prev) => ({ ...prev, [field.key]: e.target.value }))
                    }
                  />
                </Field>
              );
            })}
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
            disabled={!canSave || saveMutation.isPending}
            onClick={() => saveMutation.mutate()}
          >
            {saveMutation.isPending ? "Saving…" : "Save"}
          </PremiumButton>
        </PremiumDialogActions>
      </PremiumDialog>

      <PremiumDialog
        open={Boolean(deleteId) && showDelete}
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
              if (row && rowLabel) return `Soft-delete ${rowLabel(row)}?`;
              return "This soft-deletes the record. It will no longer appear in lists.";
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
