"use client";

import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Grid2 as Grid,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import { ArrowBack } from "@mui/icons-material";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useParams, useSearchParams } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { CommentThread } from "@/components/comments/CommentThread";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import {
  fetchVillage360,
  type Village360Profile,
  type Village360Section,
} from "@/features/villages/api";
import { Village360Orbit } from "@/features/villages/village-360-orbit";
import { formatInr } from "@/features/procurements/api";

function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <Box
      sx={{
        p: 1.5,
        borderRadius: 2,
        border: "1px solid",
        borderColor: "divider",
        bgcolor: "background.paper",
        height: "100%",
      }}
    >
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="subtitle1" fontWeight={700}>
        {value}
      </Typography>
    </Box>
  );
}

function Panel({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Box
      sx={{
        p: { xs: 2, md: 2.5 },
        borderRadius: 3,
        border: "1px solid",
        borderColor: "divider",
        bgcolor: "background.paper",
        backgroundImage: "linear-gradient(180deg, rgba(27,67,50,0.05) 0%, transparent 42%)",
      }}
    >
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      {children}
    </Box>
  );
}

function num(stats: Record<string, string | number>, key: string): string {
  const v = stats[key];
  return v == null ? "—" : String(v);
}

function renderSection(section: Village360Section, profile: Village360Profile) {
  const s = profile.statistics;
  const a = profile.analytics;

  switch (section) {
    case "overview":
      return (
        <Panel title="Village dashboard">
          <Grid container spacing={1.5}>
            {[
              ["Total farmers", num(s, "total_farmers")],
              ["Active farmers", num(s, "active_farmers")],
              ["VIP farmers", num(s, "vip_farmers")],
              ["Cultivated area", `${num(s, "total_cultivated_area")} ac`],
              ["Own farming", `${num(s, "own_farming_area")} ac`],
              ["Paddy area", `${num(s, "total_paddy_area")} ac`],
              ["Corn area", `${num(s, "total_corn_area")} ac`],
              ["Other crops", `${num(s, "total_other_crops_area")} ac`],
              ["Expected proc.", `${num(s, "expected_procurement_kg")} kg`],
              ["Actual proc.", `${num(s, "actual_procurement_kg")} kg`],
              ["Today proc.", `${num(s, "todays_procurement_kg")} kg`],
              ["Season proc.", `${num(s, "current_season_procurement_kg")} kg`],
              ["Tractor hours", num(s, "total_tractor_hours")],
              ["Rotavator hours", num(s, "total_rotavator_hours")],
              ["Cultivator hours", num(s, "total_cultivator_hours")],
              ["Baler hours", num(s, "total_baler_hours")],
              ["Bolero trips", num(s, "total_bolero_trips")],
              ["DCM trips", num(s, "total_dcm_trips")],
              ["Diesel", formatInr(num(s, "diesel_consumed"))],
              ["Outstanding", formatInr(num(s, "outstanding_payments"))],
              ["Revenue", formatInr(num(s, "revenue"))],
              ["Profit", formatInr(num(s, "profit"))],
              ["Pending collections", formatInr(num(s, "pending_collections"))],
            ].map(([label, value]) => (
              <Grid key={label} size={{ xs: 6, sm: 4, md: 3 }}>
                <StatTile label={label} value={value} />
              </Grid>
            ))}
          </Grid>

          <Typography variant="subtitle2" sx={{ mt: 3, mb: 1 }}>
            Reports
          </Typography>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            {profile.reports.map((r) => (
              <Chip key={r.code} component={Link} href={r.href} clickable label={r.title} />
            ))}
          </Stack>

          <Typography variant="subtitle2" sx={{ mt: 3, mb: 1 }}>
            Map readiness (GIS)
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Center GPS: {profile.map.village_center.lat ?? "—"}, {profile.map.village_center.lng ?? "—"} ·
            Farmer pins: {profile.map.farmer_locations_count} · Farm pins: {profile.map.farm_locations_count} ·
            Boundary layers: future · Live vehicles: future
          </Typography>
        </Panel>
      );

    case "farmers":
      return (
        <Panel title="Farmers">
          {profile.farmers.length === 0 ? (
            <Typography color="text.secondary">No farmers in this village</Typography>
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Farmer</TableCell>
                  <TableCell>Phone</TableCell>
                  <TableCell>Trust</TableCell>
                  <TableCell>Crop</TableCell>
                  <TableCell>Outstanding</TableCell>
                  <TableCell>Revenue</TableCell>
                  <TableCell />
                </TableRow>
              </TableHead>
              <TableBody>
                {profile.farmers.map((f) => (
                  <TableRow key={String(f.id)}>
                    <TableCell>{String(f.full_name)}</TableCell>
                    <TableCell>{String(f.phone_primary)}</TableCell>
                    <TableCell>{f.trust_rating != null ? String(f.trust_rating) : "—"}</TableCell>
                    <TableCell>{String(f.current_crop ?? "—")}</TableCell>
                    <TableCell>{formatInr(String(f.outstanding ?? "0"))}</TableCell>
                    <TableCell>{formatInr(String(f.lifetime_revenue ?? "0"))}</TableCell>
                    <TableCell>
                      <Button component={Link} href={String(f.profile_href)} size="small">
                        Farmer 360
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </Panel>
      );

    case "procurements":
      return (
        <Panel title="Procurement">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Crop</TableCell>
                <TableCell>Farmer</TableCell>
                <TableCell>Buyer</TableCell>
                <TableCell>Qty</TableCell>
                <TableCell>Rate</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {profile.procurements.map((p) => (
                <TableRow key={String(p.id)}>
                  <TableCell>{String(p.procurement_date)}</TableCell>
                  <TableCell>{String(p.crop_name ?? "—")}</TableCell>
                  <TableCell>{String(p.farmer_name ?? "—")}</TableCell>
                  <TableCell>{String(p.buyer_name ?? "—")}</TableCell>
                  <TableCell>{String(p.quantity_kg)} kg</TableCell>
                  <TableCell>{formatInr(String(p.rate_per_quintal ?? "0"))}</TableCell>
                  <TableCell>{String(p.status)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Panel>
      );

    case "services":
      return (
        <Panel title="Services">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Category</TableCell>
                <TableCell>Farmer</TableCell>
                <TableCell>Vehicle</TableCell>
                <TableCell>Hours</TableCell>
                <TableCell>Amount</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {profile.services.map((row) => (
                <TableRow key={String(row.id)}>
                  <TableCell>{String(row.service_date)}</TableCell>
                  <TableCell>{String(row.service_category)}</TableCell>
                  <TableCell>{String(row.farmer_name ?? "—")}</TableCell>
                  <TableCell>{String(row.vehicle_name ?? row.vehicle_type ?? "—")}</TableCell>
                  <TableCell>{String(row.hours ?? "—")}</TableCell>
                  <TableCell>{formatInr(String(row.amount_charged ?? "0"))}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Panel>
      );

    case "vehicles":
      return (
        <Panel title="Vehicles">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Vehicle</TableCell>
                <TableCell>Hours</TableCell>
                <TableCell>Trips</TableCell>
                <TableCell>Diesel</TableCell>
                <TableCell>Revenue</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {profile.vehicles.map((v, idx) => (
                <TableRow key={`${v.vehicle_name}-${idx}`}>
                  <TableCell>{String(v.vehicle_name)}</TableCell>
                  <TableCell>{String(v.hours)}</TableCell>
                  <TableCell>{String(v.trips)}</TableCell>
                  <TableCell>{formatInr(String(v.diesel))}</TableCell>
                  <TableCell>{formatInr(String(v.revenue))}</TableCell>
                  <TableCell>
                    {v.profile_href ? (
                      <Button component={Link} href={String(v.profile_href)} size="small">
                        Vehicle
                      </Button>
                    ) : null}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Panel>
      );

    case "payments":
      return (
        <Panel title="Payments">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Farmer</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Mode</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {profile.payments.map((p) => (
                <TableRow key={String(p.id)}>
                  <TableCell>{String(p.payment_date)}</TableCell>
                  <TableCell>{String(p.farmer_name ?? "—")}</TableCell>
                  <TableCell>{formatInr(String(p.amount))}</TableCell>
                  <TableCell>{String(p.payment_mode ?? "—")}</TableCell>
                  <TableCell>{String(p.status)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Panel>
      );

    case "finance":
      return (
        <Panel title="Finance">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Farmer</TableCell>
                <TableCell>Amount</TableCell>
                <TableCell>Outstanding</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {profile.finance.map((f) => (
                <TableRow key={String(f.id)}>
                  <TableCell>{String(f.loan_date)}</TableCell>
                  <TableCell>{String(f.farmer_name ?? "—")}</TableCell>
                  <TableCell>{formatInr(String(f.amount))}</TableCell>
                  <TableCell>{formatInr(String(f.outstanding))}</TableCell>
                  <TableCell>{String(f.status)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Panel>
      );

    case "farming":
      return (
        <Panel title="Farming">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Season</TableCell>
                <TableCell>Farmer</TableCell>
                <TableCell>Crop</TableCell>
                <TableCell>Area</TableCell>
                <TableCell>Stage</TableCell>
                <TableCell>Yield</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {profile.farming.map((f) => (
                <TableRow key={String(f.id)}>
                  <TableCell>
                    {String(f.season)} {String(f.year)}
                  </TableCell>
                  <TableCell>{String(f.farmer_name ?? "—")}</TableCell>
                  <TableCell>{String(f.crop_name ?? "—")}</TableCell>
                  <TableCell>{String(f.acres ?? "—")}</TableCell>
                  <TableCell>{String(f.cultivation_stage ?? "—")}</TableCell>
                  <TableCell>{String(f.actual_yield ?? "—")}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Panel>
      );

    case "buyers":
      return (
        <Panel title="Buyers">
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Buyer</TableCell>
                <TableCell>Qty</TableCell>
                <TableCell>Avg rate</TableCell>
                <TableCell>Last purchase</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {profile.buyers.map((b) => (
                <TableRow key={String(b.id)}>
                  <TableCell>{String(b.name)}</TableCell>
                  <TableCell>{String(b.quantity_purchased_kg)} kg</TableCell>
                  <TableCell>
                    {b.average_rate != null ? formatInr(String(b.average_rate)) : "—"}
                  </TableCell>
                  <TableCell>{String(b.last_purchase_date ?? "—")}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Panel>
      );

    case "comments":
      return (
        <Panel title="Comments">
          <CommentThread entityType="village" entityId={profile.summary.id} />
        </Panel>
      );

    case "documents":
      return (
        <Panel title="Documents">
          {profile.documents.length === 0 ? (
            <Typography color="text.secondary">No documents linked to this village</Typography>
          ) : (
            <Stack spacing={1}>
              {profile.documents.map((d) => (
                <Box key={d.id} sx={{ p: 1.25, borderRadius: 2, bgcolor: "rgba(0,0,0,0.02)" }}>
                  <Typography fontWeight={600}>{d.file_name}</Typography>
                  <Typography variant="caption">{d.document_type}</Typography>
                </Box>
              ))}
            </Stack>
          )}
        </Panel>
      );

    case "analytics":
      return (
        <Panel title="Analytics">
          <Grid container spacing={1.5}>
            <Grid size={{ xs: 6, md: 4 }}>
              <StatTile label="Top crop" value={a.top_crop ?? "—"} />
            </Grid>
            <Grid size={{ xs: 6, md: 4 }}>
              <StatTile label="Top farmer" value={a.top_farmer ?? "—"} />
            </Grid>
            <Grid size={{ xs: 6, md: 4 }}>
              <StatTile label="Top buyer" value={a.top_buyer ?? "—"} />
            </Grid>
            <Grid size={{ xs: 6, md: 4 }}>
              <StatTile label="Most used vehicle" value={a.most_used_vehicle ?? "—"} />
            </Grid>
            <Grid size={{ xs: 6, md: 4 }}>
              <StatTile label="Avg yield" value={a.average_yield ?? "—"} />
            </Grid>
            <Grid size={{ xs: 6, md: 4 }}>
              <StatTile
                label="Avg proc. rate"
                value={a.average_procurement_rate ? formatInr(a.average_procurement_rate) : "—"}
              />
            </Grid>
            <Grid size={{ xs: 6, md: 4 }}>
              <StatTile
                label="Avg payment delay"
                value={
                  a.average_payment_delay_days ? `${a.average_payment_delay_days} d` : "—"
                }
              />
            </Grid>
            <Grid size={{ xs: 6, md: 4 }}>
              <StatTile label="Farmer base" value={String(a.village_growth_farmers)} />
            </Grid>
          </Grid>
          {Object.keys(a.revenue_trend).length > 0 && (
            <>
              <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                Revenue trend
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {Object.entries(a.revenue_trend).map(([year, amt]) => (
                  <Chip key={year} label={`${year}: ${formatInr(amt)}`} />
                ))}
              </Stack>
            </>
          )}
          {Object.keys(a.season_comparison).length > 0 && (
            <>
              <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                Season comparison
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {Object.entries(a.season_comparison).map(([season, amt]) => (
                  <Chip key={season} label={`${season}: ${formatInr(amt)}`} />
                ))}
              </Stack>
            </>
          )}
        </Panel>
      );

    case "timeline":
      return (
        <Panel title="Timeline">
          <Stack spacing={1.5}>
            {profile.timeline.map((ev, idx) => (
              <Box key={`${ev.occurred_at}-${idx}`}>
                <Typography fontWeight={600}>{ev.title}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {new Date(ev.occurred_at).toLocaleString()} · {ev.event_type}
                </Typography>
                {ev.description && (
                  <Typography variant="body2" color="text.secondary">
                    {ev.description}
                  </Typography>
                )}
              </Box>
            ))}
          </Stack>
        </Panel>
      );

    default:
      return null;
  }
}

export default function Village360Page() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const villageId = params.id;
  const initial = (searchParams.get("tab") as Village360Section | null) ?? "overview";
  const [section, setSection] = useState<Village360Section>(initial);

  useEffect(() => {
    const tab = searchParams.get("tab") as Village360Section | null;
    if (tab) setSection(tab);
  }, [searchParams]);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["village-360", villageId],
    queryFn: () => fetchVillage360(villageId),
    enabled: Boolean(villageId),
  });

  return (
    <MuiPageShell
      title={data?.summary.name ?? "Village 360°"}
      description={
        data
          ? `${data.summary.village_code ?? "—"} · ${[data.summary.mandal, data.summary.district]
              .filter(Boolean)
              .join(" · ")}`
          : "Loading village relationship profile…"
      }
      actions={
        <Button component={Link} href="/villages" startIcon={<ArrowBack />} variant="outlined">
          All villages
        </Button>
      }
    >
      {isLoading && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      )}
      {isError && (
        <Alert severity="warning">
          {error instanceof Error ? error.message : "Could not load village 360"}
        </Alert>
      )}

      {data && (
        <Grid container spacing={3}>
          <Grid size={{ xs: 12, lg: 5 }}>
            <Box
              sx={{
                p: { xs: 2, md: 3 },
                borderRadius: 4,
                border: "1px solid",
                borderColor: "divider",
                bgcolor: "background.paper",
                position: { lg: "sticky" },
                top: { lg: 88 },
              }}
            >
              <Village360Orbit
                villageName={data.summary.name}
                villageCode={data.summary.village_code}
                status={data.summary.status}
                active={section}
                onSelect={setSection}
              />
              <Stack spacing={1} sx={{ mt: 2 }}>
                <Typography variant="body2">
                  <strong>Agent:</strong> {data.summary.agent_name ?? "—"}
                </Typography>
                <Typography variant="body2">
                  <strong>Pincode:</strong> {data.summary.pincode ?? "—"}
                </Typography>
                <Typography variant="body2">
                  <strong>Population:</strong> {data.summary.population ?? "—"}
                </Typography>
                <Typography variant="h5" color="primary.main" fontWeight={700}>
                  {formatInr(String(data.statistics.revenue ?? "0"))}{" "}
                  <Typography component="span" variant="caption" color="text.secondary">
                    revenue
                  </Typography>
                </Typography>
              </Stack>
            </Box>
          </Grid>
          <Grid size={{ xs: 12, lg: 7 }}>{renderSection(section, data)}</Grid>
        </Grid>
      )}
    </MuiPageShell>
  );
}
