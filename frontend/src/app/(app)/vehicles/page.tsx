"use client";

import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { Truck } from "lucide-react";
import { PageShell } from "@/components/shell/page-shell";
import {
  FLEET_INVENTORY_SUMMARY,
  FLEET_SERVICE_TYPES,
  FLEET_TRACTORS,
  FLEET_TRANSPORT,
  FUEL_TYPE_OPTIONS,
} from "@/constants/fleet-inventory";
import { fetchAssets } from "@/features/assets/api";
import { fetchVehicleTypes } from "@/features/master-data/api";

function fuelLabel(value: string | null | undefined): string {
  if (!value) return "—";
  return FUEL_TYPE_OPTIONS.find((o) => o.value === value)?.label ?? value;
}

export default function VehiclesPage() {
  const assetsQuery = useQuery({
    queryKey: ["fleet-assets"],
    queryFn: () => fetchAssets(1, 100),
  });
  const typesQuery = useQuery({
    queryKey: ["fleet-vehicle-types"],
    queryFn: () => fetchVehicleTypes(1, 100),
  });

  const staticCatalog = [...FLEET_SERVICE_TYPES, ...FLEET_TRACTORS, ...FLEET_TRANSPORT];
  const apiTypes = typesQuery.data?.items ?? [];
  const typeChips =
    apiTypes.length > 0
      ? apiTypes.map((t) => ({
          key: t.id,
          label: `${t.name}${t.code ? ` · ${t.code}` : ""}`,
        }))
      : staticCatalog.map((item) => ({
          key: item.code,
          label: `${item.name} · ${fuelLabel(item.fuelType)}`,
        }));

  return (
    <PageShell
      title="Vehicles"
      description={`Fleet catalog and asset instances — ${FLEET_INVENTORY_SUMMARY}. Record daily diesel cost on Field Services (tractor / transport / vehicle ops). Trip ledger comes later.`}
    >
      <Stack spacing={3}>
        <Alert severity="info" icon={<Truck size={18} />}>
          Vehicle types from <strong>GET /vehicle-types</strong> (fallback: local fleet catalog). Asset
          instances from <strong>GET /assets</strong> (migrations <code>010</code>/<code>025</code>).
          Daily diesel uses field-service <strong>Diesel cost (₹)</strong> until{" "}
          <code>vehicle_trips</code> ships.
        </Alert>

        <Box>
          <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
            Vehicle types
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
            Catalog codes used in field-service dropdowns and linked to asset instances. Manage in
            Settings → Master data → Vehicle types.
          </Typography>
          {typesQuery.isLoading && (
            <Stack direction="row" spacing={1} alignItems="center" sx={{ py: 1 }}>
              <CircularProgress size={18} />
              <Typography variant="body2">Loading types…</Typography>
            </Stack>
          )}
          {!typesQuery.isLoading && (
            <Stack direction="row" flexWrap="wrap" useFlexGap spacing={1}>
              {typeChips.map((item) => (
                <Chip key={item.key} label={item.label} variant="outlined" size="small" />
              ))}
            </Stack>
          )}
        </Box>

        <Box>
          <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
            Asset instances
          </Typography>
          {assetsQuery.isLoading && (
            <Stack direction="row" spacing={1} alignItems="center" sx={{ py: 2 }}>
              <CircularProgress size={20} />
              <Typography variant="body2">Loading assets…</Typography>
            </Stack>
          )}
          {assetsQuery.isError && (
            <Alert severity="warning">
              Could not load assets (
              {assetsQuery.error instanceof Error ? assetsQuery.error.message : "error"}). Run
              migration <code>025</code> and <code>python -m scripts.seed_services</code> if the
              table is empty.
            </Alert>
          )}
          {!assetsQuery.isLoading && !assetsQuery.isError && (assetsQuery.data?.items.length ?? 0) === 0 && (
            <Alert severity="info">
              No asset instances yet. Seed fleet units or create via POST /assets (name, number,
              type, status, fuel type, driver).
            </Alert>
          )}
          {!assetsQuery.isLoading &&
            !assetsQuery.isError &&
            (assetsQuery.data?.items.length ?? 0) > 0 && (
              <Table size="small" sx={{ bgcolor: "background.paper", borderRadius: 1 }}>
                <TableHead>
                  <TableRow>
                    <TableCell>Code</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Number</TableCell>
                    <TableCell>Fuel</TableCell>
                    <TableCell>Driver</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {assetsQuery.data!.items.map((asset) => (
                    <TableRow key={asset.id}>
                      <TableCell>{asset.asset_code}</TableCell>
                      <TableCell>{asset.name}</TableCell>
                      <TableCell>
                        {asset.vehicle_type_name ?? asset.asset_category}
                        {asset.vehicle_type_code ? ` (${asset.vehicle_type_code})` : ""}
                      </TableCell>
                      <TableCell>{asset.registration_number ?? "—"}</TableCell>
                      <TableCell>{fuelLabel(asset.fuel_type)}</TableCell>
                      <TableCell>{asset.driver_name ?? "—"}</TableCell>
                      <TableCell>
                        <Chip size="small" label={asset.status} />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
        </Box>
      </Stack>
    </PageShell>
  );
}
