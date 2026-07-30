"use client";

import {
  Card,
  CardContent,
  Stack,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { fetchHamaliDaily, fetchHamaliSummary } from "@/features/hamali/api";
import { useAuth } from "@/hooks/use-auth";

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export default function HamaliPortalPage() {
  const { role } = useAuth();
  const [tab, setTab] = useState(0);
  const workDate = todayIso();

  const dailyQuery = useQuery({
    queryKey: ["hamali", "daily", workDate],
    queryFn: () => fetchHamaliDaily(workDate),
    enabled: tab === 0,
  });

  const weekQuery = useQuery({
    queryKey: ["hamali", "summary", "week", workDate],
    queryFn: () => fetchHamaliSummary("week", workDate),
    enabled: tab === 1,
  });

  const monthQuery = useQuery({
    queryKey: ["hamali", "summary", "month", workDate],
    queryFn: () => fetchHamaliSummary("month", workDate),
    enabled: tab === 2,
  });

  const title = role === "HAMALI" ? "My work" : "Hamali portal";
  const daily = dailyQuery.data;
  const summary = tab === 1 ? weekQuery.data : tab === 2 ? monthQuery.data : undefined;
  const summaryLoading = tab === 1 ? weekQuery.isLoading : monthQuery.isLoading;

  return (
    <MuiPageShell title={title} subtitle="Bags handled and tips received (read-only)">
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 2 }}>
        <Tab label="Today" />
        <Tab label="Weekly summary" />
        <Tab label="Monthly summary" />
      </Tabs>

      {tab === 0 && (
        <Stack spacing={2}>
          <Typography variant="body2" color="text.secondary">
            Date: {workDate}
          </Typography>
          {dailyQuery.isLoading && <Typography>Loading…</Typography>}
          {daily && (
            <>
              <Stack direction="row" spacing={2}>
                <Card sx={{ flex: 1 }}>
                  <CardContent>
                    <Typography variant="overline">Bags</Typography>
                    <Typography variant="h4">{daily.total_bags}</Typography>
                  </CardContent>
                </Card>
                <Card sx={{ flex: 1 }}>
                  <CardContent>
                    <Typography variant="overline">Tips (₹)</Typography>
                    <Typography variant="h4">{daily.total_tips}</Typography>
                  </CardContent>
                </Card>
              </Stack>
              <FarmerTable rows={daily.lines} emptyLabel="No work logged for today." />
            </>
          )}
        </Stack>
      )}

      {tab > 0 && (
        <Stack spacing={2}>
          {summaryLoading && <Typography>Loading…</Typography>}
          {summary && (
            <>
              <Typography variant="body2" color="text.secondary">
                {summary.date_from} → {summary.date_to} · {summary.days_worked} day(s) worked
              </Typography>
              <Stack direction="row" spacing={2}>
                <Card sx={{ flex: 1 }}>
                  <CardContent>
                    <Typography variant="overline">Total bags</Typography>
                    <Typography variant="h4">{summary.total_bags}</Typography>
                  </CardContent>
                </Card>
                <Card sx={{ flex: 1 }}>
                  <CardContent>
                    <Typography variant="overline">Total tips (₹)</Typography>
                    <Typography variant="h4">{summary.total_tips}</Typography>
                  </CardContent>
                </Card>
              </Stack>
              <Typography variant="subtitle2">By farmer</Typography>
              <FarmerTable rows={summary.by_farmer} emptyLabel="No work in this period." />
            </>
          )}
        </Stack>
      )}
    </MuiPageShell>
  );
}

function FarmerTable({
  rows,
  emptyLabel,
}: {
  rows: { farmer_id: string; farmer_name: string; bag_count: number; tip_amount: string }[];
  emptyLabel: string;
}) {
  return (
    <Table size="small">
      <TableHead>
        <TableRow>
          <TableCell>Farmer</TableCell>
          <TableCell align="right">Bags</TableCell>
          <TableCell align="right">Tip (₹)</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map((line) => (
          <TableRow key={line.farmer_id}>
            <TableCell>{line.farmer_name}</TableCell>
            <TableCell align="right">{line.bag_count}</TableCell>
            <TableCell align="right">{line.tip_amount}</TableCell>
          </TableRow>
        ))}
        {rows.length === 0 && (
          <TableRow>
            <TableCell colSpan={3}>
              <Typography color="text.secondary">{emptyLabel}</Typography>
            </TableCell>
          </TableRow>
        )}
      </TableBody>
    </Table>
  );
}
