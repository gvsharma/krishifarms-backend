"use client";

import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  InputAdornment,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { Search, TravelExplore } from "@mui/icons-material";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useDeferredValue, useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { fetchVillages } from "@/features/master-data/api";
import { searchVillages } from "@/features/villages/api";

export default function VillagesPage() {
  const [q, setQ] = useState("");
  const deferred = useDeferredValue(q.trim());

  const listQuery = useQuery({
    queryKey: ["villages", "list", deferred],
    queryFn: () => fetchVillages(1, 100, deferred ? { q: deferred } : undefined),
    enabled: deferred.length < 2,
  });

  const searchQuery = useQuery({
    queryKey: ["villages", "search", deferred],
    queryFn: () => searchVillages(deferred),
    enabled: deferred.length >= 2,
  });

  const isSearch = deferred.length >= 2;
  const loading = isSearch ? searchQuery.isLoading : listQuery.isLoading;
  const error = isSearch ? searchQuery.error : listQuery.error;

  return (
    <MuiPageShell
      title="Villages"
      description="First-class village relationship hubs — open any village for the 360° dashboard."
      actions={
        <Button component={Link} href="/settings/villages" variant="outlined">
          Manage masters
        </Button>
      }
    >
      <Stack spacing={2}>
        <TextField
          fullWidth
          placeholder="Search village, mandal, farmer, buyer, or crop…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
        />

        {loading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Alert severity="warning">
            {error instanceof Error ? error.message : "Could not load villages"}
          </Alert>
        )}

        {!loading && !isSearch && listQuery.data && (
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Code</TableCell>
                <TableCell>Village</TableCell>
                <TableCell>Mandal</TableCell>
                <TableCell>District</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Agent</TableCell>
                <TableCell align="right">Open</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {listQuery.data.items.map((v) => (
                <TableRow key={v.id} hover>
                  <TableCell>{v.village_code ?? "—"}</TableCell>
                  <TableCell>
                    <Typography fontWeight={600}>{v.name}</Typography>
                  </TableCell>
                  <TableCell>{v.mandal ?? "—"}</TableCell>
                  <TableCell>{v.district ?? "—"}</TableCell>
                  <TableCell>
                    <Chip size="small" label={v.status ?? "active"} />
                  </TableCell>
                  <TableCell>{v.agent_name ?? "—"}</TableCell>
                  <TableCell align="right">
                    <Button
                      component={Link}
                      href={`/villages/${v.id}`}
                      size="small"
                      startIcon={<TravelExplore />}
                    >
                      360°
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}

        {!loading && isSearch && searchQuery.data && (
          <Stack spacing={1}>
            <Typography variant="body2" color="text.secondary">
              {searchQuery.data.total} match{searchQuery.data.total === 1 ? "" : "es"} for “{deferred}”
            </Typography>
            {searchQuery.data.items.map((hit) => (
              <Box
                key={hit.id}
                sx={{
                  p: 1.5,
                  borderRadius: 2,
                  border: "1px solid",
                  borderColor: "divider",
                  display: "flex",
                  justifyContent: "space-between",
                  gap: 2,
                  alignItems: "center",
                }}
              >
                <Box>
                  <Typography fontWeight={700}>{hit.name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {[hit.village_code, hit.mandal, hit.district].filter(Boolean).join(" · ")} · matched via{" "}
                    {hit.match_reason} · {hit.farmer_count} farmers
                  </Typography>
                </Box>
                <Button component={Link} href={`/villages/${hit.id}`} variant="contained" size="small">
                  Open 360°
                </Button>
              </Box>
            ))}
          </Stack>
        )}
      </Stack>
    </MuiPageShell>
  );
}
