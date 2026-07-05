"use client";

import {
  Alert,
  Box,
  Button,
  Card,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
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
import { useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { createVillage, fetchVillages } from "@/features/master-data/api";

export default function SettingsVillagesPage() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [name, setName] = useState("");
  const [nameTe, setNameTe] = useState("");
  const queryClient = useQueryClient();

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["villages"],
    queryFn: () => fetchVillages(),
  });

  const createMutation = useMutation({
    mutationFn: () => createVillage({ name: name.trim(), name_te: nameTe.trim() || null }),
    onSuccess: () => {
      setDialogOpen(false);
      setName("");
      setNameTe("");
      queryClient.invalidateQueries({ queryKey: ["villages"] });
    },
  });

  return (
    <MuiPageShell
      title="Villages"
      description="Master village list for farmer and procurement geography. CRUD stub — full edit flows in W2."
      actions={
        <Button variant="contained" startIcon={<Add />} onClick={() => setDialogOpen(true)}>
          Add village
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
          <Alert severity="warning" sx={{ m: 2 }}>
            {error instanceof Error ? error.message : "Could not load villages"}
          </Alert>
        )}

        {!isLoading && data && (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Name (EN)</TableCell>
                  <TableCell>Name (TE)</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.items.map((village) => (
                  <TableRow key={village.id} hover>
                    <TableCell>{village.name}</TableCell>
                    <TableCell>{village.name_te ?? "—"}</TableCell>
                    <TableCell>{village.is_active ? "Active" : "Inactive"}</TableCell>
                  </TableRow>
                ))}
                {data.items.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={3} align="center">
                      <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                        No villages yet
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Card>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Add village</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name (English)"
            fullWidth
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <TextField
            margin="dense"
            label="Name (Telugu)"
            fullWidth
            value={nameTe}
            onChange={(e) => setNameTe(e.target.value)}
          />
          {createMutation.isError && (
            <Alert severity="error" sx={{ mt: 1 }}>
              {createMutation.error instanceof Error
                ? createMutation.error.message
                : "Failed to create village"}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            disabled={!name.trim() || createMutation.isPending}
            onClick={() => createMutation.mutate()}
          >
            {createMutation.isPending ? "Saving…" : "Save"}
          </Button>
        </DialogActions>
      </Dialog>
    </MuiPageShell>
  );
}
