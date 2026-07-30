"use client";

import {
  Button,
  Card,
  CardContent,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { PermissionGuard } from "@/components/auth/permission-guard";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { fetchFarmers } from "@/features/farmers/api";
import {
  createHamaliWorkEntry,
  fetchHamaliWorkers,
} from "@/features/hamali/api";

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export default function HamaliWorkLogPage() {
  const queryClient = useQueryClient();
  const [workerId, setWorkerId] = useState("");
  const [farmerId, setFarmerId] = useState("");
  const [workDate, setWorkDate] = useState(todayIso());
  const [bagCount, setBagCount] = useState("0");
  const [tipAmount, setTipAmount] = useState("0");
  const [notes, setNotes] = useState("");

  const workersQuery = useQuery({
    queryKey: ["hamali", "workers"],
    queryFn: fetchHamaliWorkers,
  });
  const farmersQuery = useQuery({
    queryKey: ["farmers", "list-mini"],
    queryFn: () => fetchFarmers({ pageSize: 200 }),
  });

  const createMutation = useMutation({
    mutationFn: createHamaliWorkEntry,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["hamali"] });
      setBagCount("0");
      setTipAmount("0");
      setNotes("");
    },
  });

  return (
    <MuiPageShell
      title="Hamali work log"
      subtitle="Record bags and tips per hamali and farmer (admin / supervisor)"
    >
      <PermissionGuard permission="hamali_work:create">
        <Card>
          <CardContent>
            <Stack spacing={2} component="form" onSubmit={(e) => {
              e.preventDefault();
              if (!workerId || !farmerId) return;
              createMutation.mutate({
                worker_id: workerId,
                farmer_id: farmerId,
                work_date: workDate,
                bag_count: Number(bagCount) || 0,
                tip_amount: tipAmount || "0",
                notes: notes || undefined,
              });
            }}>
              <TextField
                select
                label="Hamali / worker"
                value={workerId}
                onChange={(e) => setWorkerId(e.target.value)}
                required
                fullWidth
              >
                {(workersQuery.data ?? []).map((w) => (
                  <MenuItem key={w.id} value={w.id}>
                    {w.full_name} ({w.worker_code})
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                select
                label="Farmer"
                value={farmerId}
                onChange={(e) => setFarmerId(e.target.value)}
                required
                fullWidth
              >
                {(farmersQuery.data?.items ?? []).map((f) => (
                  <MenuItem key={f.id} value={f.id}>
                    {f.full_name}
                  </MenuItem>
                ))}
              </TextField>
              <TextField
                label="Work date"
                type="date"
                value={workDate}
                onChange={(e) => setWorkDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                fullWidth
              />
              <Stack direction="row" spacing={2}>
                <TextField
                  label="Bags"
                  type="number"
                  value={bagCount}
                  onChange={(e) => setBagCount(e.target.value)}
                  fullWidth
                />
                <TextField
                  label="Tip (₹)"
                  type="number"
                  value={tipAmount}
                  onChange={(e) => setTipAmount(e.target.value)}
                  fullWidth
                />
              </Stack>
              <TextField
                label="Notes"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                multiline
                minRows={2}
                fullWidth
              />
              <Button type="submit" variant="contained" disabled={createMutation.isPending}>
                Save entry
              </Button>
              {createMutation.isError && (
                <Typography color="error">Could not save entry.</Typography>
              )}
              {createMutation.isSuccess && (
                <Typography color="success.main">Entry saved.</Typography>
              )}
            </Stack>
          </CardContent>
        </Card>
      </PermissionGuard>
    </MuiPageShell>
  );
}
