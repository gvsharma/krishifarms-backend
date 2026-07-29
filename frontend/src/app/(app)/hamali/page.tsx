"use client";

import {
  Alert,
  Box,
  Button,
  Card,
  Chip,
  CircularProgress,
  Stack,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { Add } from "@mui/icons-material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { PermissionGuard } from "@/components/auth/permission-guard";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { SearchableSelect } from "@/components/ui/searchable-select";
import {
  PremiumDialog,
  PremiumDialogActions,
  PremiumDialogContent,
  PremiumDialogTitle,
} from "@/components/ui/premium-dialog";
import { Button as PremiumButton, Field, Input, PREMIUM_SCOPE } from "@/components/ui/premium";
import {
  createHamaliDailyEntry,
  createHamaliWeeklyPayment,
  createHamaliWorker,
  fetchHamaliDailyEntries,
  fetchHamaliWeeklyPayments,
  fetchHamaliWeeklySummary,
  fetchHamaliWorkers,
  markHamaliWeeklyPaymentPaid,
  mondayOf,
  PAYMENT_STATUS_LABELS,
  type HamaliWorker,
} from "@/features/hamali/api";
import { formatInr } from "@/features/procurements/api";
import { TOUCH_FIELD_SX } from "@/features/field-services/work-details";

export default function HamaliPage() {
  const queryClient = useQueryClient();
  const today = useMemo(() => new Date().toISOString().slice(0, 10), []);
  const [tab, setTab] = useState(0);
  const [dateFrom, setDateFrom] = useState(mondayOf(today));
  const [dateTo, setDateTo] = useState(today);
  const [weekStart, setWeekStart] = useState(mondayOf(today));

  const [entryOpen, setEntryOpen] = useState(false);
  const [workerOpen, setWorkerOpen] = useState(false);
  const [entryWorkerId, setEntryWorkerId] = useState("");
  const [entryDate, setEntryDate] = useState(today);
  const [bagsLifted, setBagsLifted] = useState("");
  const [maintenance, setMaintenance] = useState("0");
  const [tip, setTip] = useState("0");
  const [entryNotes, setEntryNotes] = useState("");
  const [newWorkerName, setNewWorkerName] = useState("");
  const [newWorkerPhone, setNewWorkerPhone] = useState("");

  const workersQuery = useQuery({
    queryKey: ["hamali-workers"],
    queryFn: () => fetchHamaliWorkers({ pageSize: 200, status: "active" }),
  });

  const entriesQuery = useQuery({
    queryKey: ["hamali-daily", dateFrom, dateTo],
    queryFn: () => fetchHamaliDailyEntries({ date_from: dateFrom, date_to: dateTo, pageSize: 100 }),
    enabled: tab === 0,
  });

  const weeklySummaryQuery = useQuery({
    queryKey: ["hamali-weekly-summary", weekStart],
    queryFn: () => fetchHamaliWeeklySummary(weekStart),
    enabled: tab === 2,
  });

  const weeklyPaymentsQuery = useQuery({
    queryKey: ["hamali-weekly-payments"],
    queryFn: () => fetchHamaliWeeklyPayments({ pageSize: 20 }),
    enabled: tab === 2,
  });

  const workers = workersQuery.data?.items ?? [];
  const selectedWorker = workers.find((w) => w.id === entryWorkerId);

  const laborPreview =
    (Number(bagsLifted) || 0) *
    Number(selectedWorker?.default_rate_per_bag ?? 20);

  const createEntryMut = useMutation({
    mutationFn: () =>
      createHamaliDailyEntry({
        hamali_worker_id: entryWorkerId,
        entry_date: entryDate,
        bags_lifted: Number(bagsLifted) || 0,
        maintenance_amount: maintenance.trim() || "0",
        tip_amount: tip.trim() || "0",
        notes: entryNotes.trim() || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["hamali-daily"] });
      queryClient.invalidateQueries({ queryKey: ["hamali-weekly-summary"] });
      setEntryOpen(false);
      setBagsLifted("");
      setMaintenance("0");
      setTip("0");
      setEntryNotes("");
    },
  });

  const createWorkerMut = useMutation({
    mutationFn: () =>
      createHamaliWorker({
        full_name: newWorkerName.trim(),
        phone: newWorkerPhone.trim() || null,
      }),
    onSuccess: (worker: HamaliWorker) => {
      queryClient.invalidateQueries({ queryKey: ["hamali-workers"] });
      setEntryWorkerId(worker.id);
      setWorkerOpen(false);
      setNewWorkerName("");
      setNewWorkerPhone("");
    },
  });

  const createWeeklyMut = useMutation({
    mutationFn: () => createHamaliWeeklyPayment({ week_start_date: weekStart }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["hamali-weekly-payments"] });
      queryClient.invalidateQueries({ queryKey: ["hamali-weekly-summary"] });
      queryClient.invalidateQueries({ queryKey: ["hamali-daily"] });
    },
  });

  const markPaidMut = useMutation({
    mutationFn: (paymentId: string) => markHamaliWeeklyPaymentPaid(paymentId, {}),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["hamali-weekly-payments"] });
      queryClient.invalidateQueries({ queryKey: ["hamali-daily"] });
    },
  });

  const summary = entriesQuery.data?.summary;

  return (
    <MuiPageShell
      title="Hamali charges"
      description="Track daily bag lifting (₹20/bag default), maintenance, tips, and weekly settlement."
      actions={
        tab === 0 ? (
          <PermissionGuard permission="hamali:create">
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => {
                createEntryMut.reset();
                setEntryOpen(true);
              }}
              sx={{ minHeight: 44 }}
            >
              Log daily work
            </Button>
          </PermissionGuard>
        ) : tab === 1 ? (
          <PermissionGuard permission="hamali:create">
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => {
                createWorkerMut.reset();
                setWorkerOpen(true);
              }}
              sx={{ minHeight: 44 }}
            >
              Add hamali worker
            </Button>
          </PermissionGuard>
        ) : null
      }
    >
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab label="Daily entries" />
        <Tab label="Workers" />
        <Tab label="Weekly payments" />
      </Tabs>

      {tab === 0 && (
        <Stack spacing={2}>
          <Card sx={{ p: 2 }}>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems="flex-end">
              <TextField
                label="From"
                type="date"
                size="small"
                InputLabelProps={{ shrink: true }}
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
              />
              <TextField
                label="To"
                type="date"
                size="small"
                InputLabelProps={{ shrink: true }}
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
              />
            </Stack>
            {summary && (
              <Stack direction="row" flexWrap="wrap" gap={2} sx={{ mt: 2 }}>
                <Stat label="Bags" value={String(summary.total_bags)} />
                <Stat label="Labor" value={formatInr(summary.total_labor_amount)} />
                <Stat label="Maintenance" value={formatInr(summary.total_maintenance_amount)} />
                <Stat label="Tips" value={formatInr(summary.total_tip_amount)} />
                <Stat label="Total" value={formatInr(summary.total_amount)} highlight />
              </Stack>
            )}
          </Card>

          {entriesQuery.isLoading && (
            <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
              <CircularProgress />
            </Box>
          )}

          {entriesQuery.data && (
            <TableContainer component={Card}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>Worker</TableCell>
                    <TableCell align="right">Bags</TableCell>
                    <TableCell align="right">Labor</TableCell>
                    <TableCell align="right">Maint.</TableCell>
                    <TableCell align="right">Tip</TableCell>
                    <TableCell align="right">Total</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {entriesQuery.data.items.map((row) => (
                    <TableRow key={row.id}>
                      <TableCell>{row.entry_date}</TableCell>
                      <TableCell>
                        {row.worker_name ?? "—"}
                        <Typography variant="caption" display="block" color="text.secondary">
                          {row.worker_code}
                        </Typography>
                      </TableCell>
                      <TableCell align="right">{row.bags_lifted}</TableCell>
                      <TableCell align="right">{formatInr(row.labor_amount)}</TableCell>
                      <TableCell align="right">{formatInr(row.maintenance_amount)}</TableCell>
                      <TableCell align="right">{formatInr(row.tip_amount)}</TableCell>
                      <TableCell align="right">{formatInr(row.total_amount)}</TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={PAYMENT_STATUS_LABELS[row.payment_status]}
                          color={
                            row.payment_status === "paid"
                              ? "success"
                              : row.payment_status === "scheduled"
                                ? "info"
                                : "warning"
                          }
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                  {entriesQuery.data.items.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={8} align="center">
                        No entries in this date range
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Stack>
      )}

      {tab === 1 && (
        <TableContainer component={Card}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Code</TableCell>
                <TableCell>Name</TableCell>
                <TableCell>Phone</TableCell>
                <TableCell align="right">Rate / bag</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(workersQuery.data?.items ?? []).map((w) => (
                <TableRow key={w.id}>
                  <TableCell>{w.worker_code}</TableCell>
                  <TableCell>{w.full_name}</TableCell>
                  <TableCell>{w.phone ?? "—"}</TableCell>
                  <TableCell align="right">{formatInr(w.default_rate_per_bag)}</TableCell>
                  <TableCell>
                    <Chip size="small" label={w.status} color={w.status === "active" ? "success" : "default"} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {tab === 2 && (
        <Stack spacing={2}>
          <Card sx={{ p: 2 }}>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems="flex-end">
              <TextField
                label="Week starting (Monday)"
                type="date"
                size="small"
                InputLabelProps={{ shrink: true }}
                value={weekStart}
                onChange={(e) => setWeekStart(mondayOf(e.target.value))}
              />
              <PermissionGuard permission="hamali:pay">
                <Button
                  variant="contained"
                  disabled={createWeeklyMut.isPending || (weeklySummaryQuery.data?.pending_entries ?? 0) === 0}
                  onClick={() => createWeeklyMut.mutate()}
                >
                  {createWeeklyMut.isPending ? "Creating…" : "Create weekly batch"}
                </Button>
              </PermissionGuard>
            </Stack>

            {weeklySummaryQuery.data && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  Week {weeklySummaryQuery.data.week_start_date} → {weeklySummaryQuery.data.week_end_date} ·{" "}
                  {weeklySummaryQuery.data.pending_entries} pending entries
                </Typography>
                <Stack direction="row" flexWrap="wrap" gap={2}>
                  <Stat label="Bags" value={String(weeklySummaryQuery.data.total_bags)} />
                  <Stat label="Labor" value={formatInr(weeklySummaryQuery.data.total_labor_amount)} />
                  <Stat label="Maintenance" value={formatInr(weeklySummaryQuery.data.total_maintenance_amount)} />
                  <Stat label="Tips" value={formatInr(weeklySummaryQuery.data.total_tip_amount)} />
                  <Stat label="Payable" value={formatInr(weeklySummaryQuery.data.total_amount)} highlight />
                </Stack>
                {weeklySummaryQuery.data.by_worker.length > 0 && (
                  <Table size="small" sx={{ mt: 2 }}>
                    <TableHead>
                      <TableRow>
                        <TableCell>Worker</TableCell>
                        <TableCell align="right">Days</TableCell>
                        <TableCell align="right">Bags</TableCell>
                        <TableCell align="right">Total</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {weeklySummaryQuery.data.by_worker.map((w) => (
                        <TableRow key={w.hamali_worker_id}>
                          <TableCell>{w.worker_name}</TableCell>
                          <TableCell align="right">{w.days_worked}</TableCell>
                          <TableCell align="right">{w.total_bags}</TableCell>
                          <TableCell align="right">{formatInr(w.total_amount)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </Box>
            )}
            {createWeeklyMut.isError && (
              <Alert severity="error" sx={{ mt: 1 }}>
                {createWeeklyMut.error instanceof Error ? createWeeklyMut.error.message : "Failed"}
              </Alert>
            )}
          </Card>

          <TableContainer component={Card}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Batch</TableCell>
                  <TableCell>Week</TableCell>
                  <TableCell align="right">Bags</TableCell>
                  <TableCell align="right">Total</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell />
                </TableRow>
              </TableHead>
              <TableBody>
                {(weeklyPaymentsQuery.data?.items ?? []).map((p) => (
                  <TableRow key={p.id}>
                    <TableCell>{p.payment_number}</TableCell>
                    <TableCell>
                      {p.week_start_date} → {p.week_end_date}
                    </TableCell>
                    <TableCell align="right">{p.total_bags}</TableCell>
                    <TableCell align="right">{formatInr(p.total_amount)}</TableCell>
                    <TableCell>
                      <Chip size="small" label={p.status} color={p.status === "paid" ? "success" : "warning"} />
                    </TableCell>
                    <TableCell align="right">
                      {p.status === "draft" && (
                        <PermissionGuard permission="hamali:pay">
                          <Button
                            size="small"
                            onClick={() => markPaidMut.mutate(p.id)}
                            disabled={markPaidMut.isPending}
                          >
                            Mark paid
                          </Button>
                        </PermissionGuard>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Stack>
      )}

      <PremiumDialog open={entryOpen} onClose={() => setEntryOpen(false)} maxWidth="sm">
        <PremiumDialogTitle>Log daily hamali work</PremiumDialogTitle>
        <PremiumDialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <SearchableSelect
              options={workers}
              getOptionLabel={(w) => `${w.full_name} (${w.worker_code})`}
              isOptionEqualToValue={(a, b) => a.id === b.id}
              value={workers.find((w) => w.id === entryWorkerId) ?? null}
              onChange={(w) => setEntryWorkerId(w?.id ?? "")}
              label="Hamali worker"
              required
              sx={TOUCH_FIELD_SX}
            />
            <TextField
              label="Date"
              type="date"
              required
              InputLabelProps={{ shrink: true }}
              sx={TOUCH_FIELD_SX}
              value={entryDate}
              onChange={(e) => setEntryDate(e.target.value)}
            />
            <TextField
              label="Bags lifted"
              type="number"
              required
              sx={TOUCH_FIELD_SX}
              inputProps={{ min: 0 }}
              value={bagsLifted}
              onChange={(e) => setBagsLifted(e.target.value)}
            />
            <TextField
              label="Maintenance charges (₹)"
              type="number"
              sx={TOUCH_FIELD_SX}
              inputProps={{ min: 0, step: 0.01 }}
              value={maintenance}
              onChange={(e) => setMaintenance(e.target.value)}
            />
            <TextField
              label="Tip (₹)"
              type="number"
              sx={TOUCH_FIELD_SX}
              inputProps={{ min: 0, step: 0.01 }}
              value={tip}
              onChange={(e) => setTip(e.target.value)}
            />
            <TextField
              label="Notes"
              multiline
              minRows={2}
              sx={TOUCH_FIELD_SX}
              value={entryNotes}
              onChange={(e) => setEntryNotes(e.target.value)}
            />
            <Alert severity="info" icon={false}>
              Labor: <strong>{formatInr(laborPreview)}</strong> ({bagsLifted || 0} bags × ₹
              {selectedWorker?.default_rate_per_bag ?? "20"})
            </Alert>
            {createEntryMut.isError && (
              <Alert severity="error">
                {createEntryMut.error instanceof Error ? createEntryMut.error.message : "Save failed"}
              </Alert>
            )}
          </Stack>
        </PremiumDialogContent>
        <PremiumDialogActions className={PREMIUM_SCOPE}>
          <PremiumButton variant="secondary" size="sm" onClick={() => setEntryOpen(false)}>
            Cancel
          </PremiumButton>
          <PremiumButton
            variant="primary"
            size="sm"
            disabled={!entryWorkerId || !bagsLifted || createEntryMut.isPending}
            onClick={() => createEntryMut.mutate()}
          >
            {createEntryMut.isPending ? "Saving…" : "Save entry"}
          </PremiumButton>
        </PremiumDialogActions>
      </PremiumDialog>

      <PremiumDialog open={workerOpen} onClose={() => setWorkerOpen(false)} maxWidth="xs">
        <PremiumDialogTitle>Add hamali worker</PremiumDialogTitle>
        <PremiumDialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <Field label="Full name" required>
              <Input value={newWorkerName} onChange={(e) => setNewWorkerName(e.target.value)} autoFocus />
            </Field>
            <Field label="Phone">
              <Input value={newWorkerPhone} onChange={(e) => setNewWorkerPhone(e.target.value)} />
            </Field>
            <Typography variant="caption" color="text.secondary">
              Default pay: ₹20 per bag lifted (editable per worker later).
            </Typography>
            {createWorkerMut.isError && (
              <Alert severity="error">
                {createWorkerMut.error instanceof Error ? createWorkerMut.error.message : "Save failed"}
              </Alert>
            )}
          </Stack>
        </PremiumDialogContent>
        <PremiumDialogActions className={PREMIUM_SCOPE}>
          <PremiumButton variant="secondary" size="sm" onClick={() => setWorkerOpen(false)}>
            Cancel
          </PremiumButton>
          <PremiumButton
            variant="primary"
            size="sm"
            disabled={newWorkerName.trim().length < 2 || createWorkerMut.isPending}
            onClick={() => createWorkerMut.mutate()}
          >
            {createWorkerMut.isPending ? "Saving…" : "Save worker"}
          </PremiumButton>
        </PremiumDialogActions>
      </PremiumDialog>
    </MuiPageShell>
  );
}

function Stat({
  label,
  value,
  highlight,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <Box>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography variant={highlight ? "h6" : "body1"} fontWeight={highlight ? 700 : 500}>
        {value}
      </Typography>
    </Box>
  );
}
