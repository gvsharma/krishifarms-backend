"use client";

import {
  Alert,
  Box,
  Button,
  Card,
  Chip,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { Add, Search } from "@mui/icons-material";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { fetchFarmers } from "@/features/farmers/api";

export default function FarmersPage() {
  const searchParams = useSearchParams();
  const villageFromUrl = searchParams.get("village_id") ?? undefined;
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["farmers", query, villageFromUrl],
    queryFn: () => fetchFarmers({ q: query || undefined, villageId: villageFromUrl }),
  });

  return (
    <MuiPageShell
      title="Farmers"
      description="Farmer registry with village assignments and outstanding balances."
      actions={
        <Button component={Link} href="/farmers/new" variant="contained" startIcon={<Add />}>
          Add farmer
        </Button>
      }
    >
      <Card sx={{ mb: 2, p: 2 }}>
        <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
          <TextField
            size="small"
            placeholder="Search name, phone, or code…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && setQuery(search.trim())}
            sx={{ flex: 1, maxWidth: 420 }}
          />
          <Button variant="outlined" startIcon={<Search />} onClick={() => setQuery(search.trim())}>
            Search
          </Button>
        </Box>
      </Card>

      <Card sx={{ overflow: "hidden" }}>
        {isLoading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
            <CircularProgress />
          </Box>
        )}

        {isError && (
          <Alert severity="warning" sx={{ m: 2 }}>
            {error instanceof Error ? error.message : "Could not load farmers"}
          </Alert>
        )}

        {!isLoading && data && (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Code</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell>Village</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Tags</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.items.map((farmer) => (
                  <TableRow key={farmer.id} hover component={Link} href={`/farmers/${farmer.id}`} sx={{ cursor: "pointer", textDecoration: "none" }}>
                    <TableCell>{farmer.farmer_code}</TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight={600}>
                        {farmer.full_name}
                      </Typography>
                      {farmer.full_name_te && (
                        <Typography variant="caption" color="text.secondary">
                          {farmer.full_name_te}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>{farmer.phone_primary}</TableCell>
                    <TableCell>{farmer.village_name ?? "—"}</TableCell>
                    <TableCell>{farmer.status}</TableCell>
                    <TableCell>
                      {farmer.tags.map((tag) => (
                        <Chip key={tag} label={tag} size="small" sx={{ mr: 0.5 }} />
                      ))}
                    </TableCell>
                  </TableRow>
                ))}
                {data.items.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                        No farmers found
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Card>
    </MuiPageShell>
  );
}
