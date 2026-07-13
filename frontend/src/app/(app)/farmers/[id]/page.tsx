"use client";

import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Grid2 as Grid,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { ArrowBack, EditOutlined, Star } from "@mui/icons-material";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState, type ReactNode } from "react";
import { CommentThread } from "@/components/comments/CommentThread";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import {
  Button as PremiumButton,
  Field as PremiumField,
  Input,
  PREMIUM_SCOPE,
  Scope,
} from "@/components/ui/premium";
import {
  PremiumDialog,
  PremiumDialogActions,
  PremiumDialogContent,
  PremiumDialogTitle,
} from "@/components/ui/premium-dialog";
import { SoftAlert } from "@/components/ui/soft-alert";
import {
  fetchFarmer,
  fetchFarmer360,
  updateFarmer,
  type Farmer360Profile,
  type Farmer360Section,
  type FarmerDetail,
} from "@/features/farmers/api";
import { Farmer360Orbit } from "@/features/farmers/farmer-360-orbit";
import {
  EMPTY_LOCATION_CASCADE,
  LocationCascade,
  type LocationCascadeValue,
} from "@/features/master-data/location-cascade";
import { formatInr } from "@/features/procurements/api";

type EditForm = {
  fullName: string;
  fullNameTe: string;
  phone: string;
  phoneSecondary: string;
  address: string;
  notes: string;
  status: string;
  preferredLanguage: string;
  preferredPaymentCycle: string;
  preferredPaymentMethod: string;
  trustRating: string;
  isVip: boolean;
  location: LocationCascadeValue;
};

function formFromFarmer(farmer: FarmerDetail): EditForm {
  return {
    fullName: farmer.full_name,
    fullNameTe: farmer.full_name_te ?? "",
    phone: farmer.phone_primary,
    phoneSecondary: farmer.phone_secondary ?? "",
    address: farmer.address ?? "",
    notes: farmer.notes ?? "",
    status: farmer.status,
    preferredLanguage: farmer.preferred_language ?? "",
    preferredPaymentCycle: farmer.preferred_payment_cycle ?? "",
    preferredPaymentMethod: farmer.preferred_payment_method ?? "",
    trustRating: farmer.trust_rating != null ? String(farmer.trust_rating) : "",
    isVip: Boolean(farmer.is_vip),
    location: {
      ...EMPTY_LOCATION_CASCADE,
      villageId: farmer.village_id,
    },
  };
}

function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <Box
      sx={{
        p: 1.5,
        borderRadius: 2,
        bgcolor: "background.paper",
        border: "1px solid",
        borderColor: "divider",
        height: "100%",
      }}
    >
      <Typography variant="caption" color="text.secondary" display="block">
        {label}
      </Typography>
      <Typography variant="subtitle1" fontWeight={700} sx={{ mt: 0.25 }}>
        {value}
      </Typography>
    </Box>
  );
}

function SectionPanel({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <Box
      sx={{
        p: { xs: 2, md: 2.5 },
        borderRadius: 3,
        bgcolor: "background.paper",
        border: "1px solid",
        borderColor: "divider",
        backgroundImage:
          "linear-gradient(180deg, rgba(45,106,79,0.04) 0%, transparent 48%)",
      }}
    >
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      {children}
    </Box>
  );
}

function EmptyNote({ text }: { text: string }) {
  return (
    <Typography variant="body2" color="text.secondary">
      {text}
    </Typography>
  );
}

function renderSection(section: Farmer360Section, profile: Farmer360Profile, farmerId: string) {
  const s = profile.statistics;
  const a = profile.analytics;
  const intel = profile.crop_intelligence;

  switch (section) {
    case "overview":
      return (
        <SectionPanel title="Relationship overview">
          <Grid container spacing={1.5}>
            <Grid size={{ xs: 6, sm: 4, md: 3 }}>
              <StatTile label="Lifetime value" value={formatInr(s.lifetime_business_value)} />
            </Grid>
            <Grid size={{ xs: 6, sm: 4, md: 3 }}>
              <StatTile label="Outstanding" value={formatInr(s.outstanding_amount)} />
            </Grid>
            <Grid size={{ xs: 6, sm: 4, md: 3 }}>
              <StatTile label="Amount paid" value={formatInr(s.amount_paid)} />
            </Grid>
            <Grid size={{ xs: 6, sm: 4, md: 3 }}>
              <StatTile label="Services" value={String(s.total_services_availed)} />
            </Grid>
            <Grid size={{ xs: 6, sm: 4, md: 3 }}>
              <StatTile label="Farming area" value={`${s.total_farming_area} ac`} />
            </Grid>
            <Grid size={{ xs: 6, sm: 4, md: 3 }}>
              <StatTile label="Crops sold" value={String(s.total_crops_sold)} />
            </Grid>
            <Grid size={{ xs: 6, sm: 4, md: 3 }}>
              <StatTile label="Proc. qty" value={`${s.total_procurement_quantity_kg} kg`} />
            </Grid>
            <Grid size={{ xs: 6, sm: 4, md: 3 }}>
              <StatTile label="Season proc." value={`${s.current_season_procurement_kg} kg`} />
            </Grid>
            <Grid size={{ xs: 6, sm: 4, md: 3 }}>
              <StatTile label="Current crop" value={s.current_crop ?? "—"} />
            </Grid>
            <Grid size={{ xs: 6, sm: 4, md: 3 }}>
              <StatTile label="Preferred vehicle" value={s.preferred_vehicle ?? "—"} />
            </Grid>
            <Grid size={{ xs: 6, sm: 4, md: 3 }}>
              <StatTile label="Last service" value={s.last_service_date ?? "—"} />
            </Grid>
            <Grid size={{ xs: 6, sm: 4, md: 3 }}>
              <StatTile label="Last payment" value={s.last_payment_date ?? "—"} />
            </Grid>
          </Grid>

          <Typography variant="subtitle2" sx={{ mt: 3, mb: 1 }}>
            Crop intelligence
          </Typography>
          <Grid container spacing={1.5}>
            <Grid size={{ xs: 6, md: 4 }}>
              <StatTile label="Most cultivated" value={intel.most_cultivated_crop ?? "—"} />
            </Grid>
            <Grid size={{ xs: 6, md: 4 }}>
              <StatTile label="Preferred buyer" value={intel.preferred_buyer ?? "—"} />
            </Grid>
            <Grid size={{ xs: 6, md: 4 }}>
              <StatTile label="Most profitable" value={intel.most_profitable_crop ?? "—"} />
            </Grid>
            <Grid size={{ xs: 6, md: 4 }}>
              <StatTile label="Avg yield" value={intel.average_yield ?? "—"} />
            </Grid>
            <Grid size={{ xs: 6, md: 4 }}>
              <StatTile label="Selling season" value={intel.preferred_selling_season ?? "—"} />
            </Grid>
            <Grid size={{ xs: 6, md: 4 }}>
              <StatTile label="Proc. frequency" value={String(intel.procurement_frequency)} />
            </Grid>
          </Grid>

          {profile.recommendations.length > 0 && (
            <>
              <Typography variant="subtitle2" sx={{ mt: 3, mb: 1 }}>
                Recommendations
              </Typography>
              <Stack spacing={1}>
                {profile.recommendations.map((rec) => (
                  <Box
                    key={rec.code}
                    sx={{
                      p: 1.5,
                      borderRadius: 2,
                      bgcolor: "rgba(45,106,79,0.06)",
                      display: "flex",
                      justifyContent: "space-between",
                      gap: 2,
                      flexWrap: "wrap",
                    }}
                  >
                    <Box>
                      <Typography fontWeight={600}>{rec.title}</Typography>
                      <Typography variant="body2" color="text.secondary">
                        {rec.rationale}
                      </Typography>
                    </Box>
                    <Chip size="small" label={rec.priority} />
                  </Box>
                ))}
              </Stack>
            </>
          )}
        </SectionPanel>
      );

    case "timeline":
      return (
        <SectionPanel title="Relationship timeline">
          {profile.timeline.length === 0 ? (
            <EmptyNote text="No timeline events yet" />
          ) : (
            <Stack spacing={1.5}>
              {profile.timeline.map((ev, idx) => (
                <Box
                  key={`${ev.event_type}-${ev.occurred_at}-${idx}`}
                  sx={{
                    display: "grid",
                    gridTemplateColumns: "12px 1fr",
                    gap: 1.5,
                  }}
                >
                  <Box
                    sx={{
                      width: 10,
                      height: 10,
                      borderRadius: "50%",
                      bgcolor: "primary.main",
                      mt: 0.7,
                    }}
                  />
                  <Box>
                    <Typography fontWeight={600}>{ev.title}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(ev.occurred_at).toLocaleString()} · {ev.event_type}
                    </Typography>
                    {ev.description && (
                      <Typography variant="body2" color="text.secondary">
                        {ev.description}
                      </Typography>
                    )}
                    {ev.amount != null && (
                      <Typography variant="body2">{formatInr(String(ev.amount))}</Typography>
                    )}
                  </Box>
                </Box>
              ))}
            </Stack>
          )}
        </SectionPanel>
      );

    case "services":
      return (
        <SectionPanel title="Services history">
          {profile.services.length === 0 ? (
            <EmptyNote text="No services recorded" />
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Vehicle</TableCell>
                  <TableCell>Hours</TableCell>
                  <TableCell>Diesel</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Payment</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {profile.services.map((row) => (
                  <TableRow key={String(row.id)}>
                    <TableCell>{String(row.service_date)}</TableCell>
                    <TableCell>{String(row.service_category)}</TableCell>
                    <TableCell>
                      {String(row.vehicle_name ?? row.vehicle_type ?? "—")}
                    </TableCell>
                    <TableCell>{String(row.hours ?? "—")}</TableCell>
                    <TableCell>{formatInr(String(row.diesel_amount ?? "0"))}</TableCell>
                    <TableCell>{formatInr(String(row.amount_charged ?? "0"))}</TableCell>
                    <TableCell>{String(row.payment_status)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </SectionPanel>
      );

    case "farming":
      return (
        <SectionPanel title="Farming history">
          {profile.farming.length === 0 ? (
            <EmptyNote text="No crop history yet" />
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Season</TableCell>
                  <TableCell>Crop</TableCell>
                  <TableCell>Area</TableCell>
                  <TableCell>Stage</TableCell>
                  <TableCell>Yield</TableCell>
                  <TableCell>Market</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {profile.farming.map((row) => (
                  <TableRow key={String(row.id)}>
                    <TableCell>
                      {String(row.season)} {String(row.year)}
                    </TableCell>
                    <TableCell>{String(row.crop_type_name ?? "—")}</TableCell>
                    <TableCell>{String(row.acres ?? "—")}</TableCell>
                    <TableCell>{String(row.cultivation_stage ?? "—")}</TableCell>
                    <TableCell>{String(row.actual_yield ?? row.expected_yield ?? "—")}</TableCell>
                    <TableCell>{String(row.selling_market ?? "—")}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </SectionPanel>
      );

    case "procurements":
      return (
        <SectionPanel title="Procurement history">
          {profile.procurements.length === 0 ? (
            <EmptyNote text="No procurements" />
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Crop</TableCell>
                  <TableCell>Qty</TableCell>
                  <TableCell>Rate</TableCell>
                  <TableCell>Buyer</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {profile.procurements.map((row) => (
                  <TableRow key={String(row.id)}>
                    <TableCell>{String(row.procurement_date)}</TableCell>
                    <TableCell>{String(row.crop_name ?? "—")}</TableCell>
                    <TableCell>{String(row.quantity_kg)} kg</TableCell>
                    <TableCell>{formatInr(String(row.rate_per_quintal ?? "0"))}</TableCell>
                    <TableCell>{String(row.buyer_name ?? "—")}</TableCell>
                    <TableCell>{String(row.status)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </SectionPanel>
      );

    case "finance":
      return (
        <SectionPanel title="Finance history">
          {profile.finance.length === 0 ? (
            <EmptyNote text="No agri-finance records" />
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Paid</TableCell>
                  <TableCell>Outstanding</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Purpose</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {profile.finance.map((row) => (
                  <TableRow key={String(row.id)}>
                    <TableCell>{String(row.loan_date)}</TableCell>
                    <TableCell>{formatInr(String(row.amount))}</TableCell>
                    <TableCell>{formatInr(String(row.paid_amount))}</TableCell>
                    <TableCell>{formatInr(String(row.outstanding))}</TableCell>
                    <TableCell>{String(row.status)}</TableCell>
                    <TableCell>{String(row.purpose ?? "—")}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </SectionPanel>
      );

    case "ledger":
      return (
        <SectionPanel title="Payment ledger">
          {profile.ledger.length === 0 ? (
            <EmptyNote text="No ledger entries" />
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Date</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Debit</TableCell>
                  <TableCell>Credit</TableCell>
                  <TableCell>Balance</TableCell>
                  <TableCell>Mode</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {profile.ledger.map((row) => (
                  <TableRow key={String(row.id)}>
                    <TableCell>{String(row.entry_date)}</TableCell>
                    <TableCell>{String(row.entry_type)}</TableCell>
                    <TableCell>{formatInr(String(row.debit))}</TableCell>
                    <TableCell>{formatInr(String(row.credit))}</TableCell>
                    <TableCell>{formatInr(String(row.balance_after))}</TableCell>
                    <TableCell>{String(row.payment_mode ?? "—")}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </SectionPanel>
      );

    case "land":
      return (
        <SectionPanel title="Land information">
          {profile.land.length === 0 ? (
            <EmptyNote text="No land parcels" />
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Survey #</TableCell>
                  <TableCell>Area</TableCell>
                  <TableCell>Ownership</TableCell>
                  <TableCell>Irrigation</TableCell>
                  <TableCell>Soil</TableCell>
                  <TableCell>GPS</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {profile.land.map((parcel) => (
                  <TableRow key={parcel.id}>
                    <TableCell>{parcel.survey_number}</TableCell>
                    <TableCell>{parcel.acres} ac</TableCell>
                    <TableCell>{parcel.ownership ?? parcel.land_type ?? "—"}</TableCell>
                    <TableCell>{parcel.irrigation_type ?? "—"}</TableCell>
                    <TableCell>{parcel.soil_type ?? "—"}</TableCell>
                    <TableCell>
                      {parcel.geo_lat && parcel.geo_lng
                        ? `${parcel.geo_lat}, ${parcel.geo_lng}`
                        : "—"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </SectionPanel>
      );

    case "documents":
      return (
        <SectionPanel title="Documents & attachments">
          {profile.documents.length === 0 ? (
            <EmptyNote text="No documents linked" />
          ) : (
            <Stack spacing={1}>
              {profile.documents.map((doc) => (
                <Box
                  key={doc.id}
                  sx={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 2,
                    p: 1.25,
                    borderRadius: 2,
                    bgcolor: "rgba(0,0,0,0.02)",
                  }}
                >
                  <Box>
                    <Typography fontWeight={600}>{doc.file_name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {doc.document_type} · {doc.mime_type}
                    </Typography>
                  </Box>
                  <Chip size="small" label={doc.link_role ?? "attachment"} />
                </Box>
              ))}
            </Stack>
          )}
        </SectionPanel>
      );

    case "communication":
      return (
        <SectionPanel title="Communication">
          <CommentThread entityType="farmer" entityId={farmerId} />
          {profile.communication.length > 0 && (
            <Stack spacing={1} sx={{ mt: 2 }}>
              {profile.communication.map((c) => (
                <Box key={c.id} sx={{ p: 1.25, borderRadius: 2, bgcolor: "rgba(0,0,0,0.02)" }}>
                  <Typography variant="caption" color="text.secondary">
                    {c.author_name ?? "User"} · {new Date(c.created_at).toLocaleString()}
                  </Typography>
                  <Typography variant="body2">{c.body}</Typography>
                </Box>
              ))}
            </Stack>
          )}
        </SectionPanel>
      );

    case "analytics":
      return (
        <SectionPanel title="Analytics">
          <Grid container spacing={1.5}>
            <Grid size={{ xs: 6, md: 3 }}>
              <StatTile label="Total revenue" value={formatInr(a.total_revenue)} />
            </Grid>
            <Grid size={{ xs: 6, md: 3 }}>
              <StatTile label="Diesel" value={formatInr(a.total_diesel_consumed)} />
            </Grid>
            <Grid size={{ xs: 6, md: 3 }}>
              <StatTile label="Tractor hours" value={String(a.total_tractor_hours)} />
            </Grid>
            <Grid size={{ xs: 6, md: 3 }}>
              <StatTile label="Trips" value={String(a.total_trips)} />
            </Grid>
            <Grid size={{ xs: 6, md: 3 }}>
              <StatTile
                label="Avg payment delay"
                value={a.average_payment_delay_days ? `${a.average_payment_delay_days} d` : "—"}
              />
            </Grid>
            <Grid size={{ xs: 6, md: 3 }}>
              <StatTile
                label="Avg proc. rate"
                value={a.average_procurement_rate ? formatInr(a.average_procurement_rate) : "—"}
              />
            </Grid>
            <Grid size={{ xs: 6, md: 3 }}>
              <StatTile
                label="Avg service cost"
                value={a.average_service_cost ? formatInr(a.average_service_cost) : "—"}
              />
            </Grid>
            <Grid size={{ xs: 6, md: 3 }}>
              <StatTile label="Outstanding" value={formatInr(a.current_outstanding)} />
            </Grid>
          </Grid>
          {Object.keys(a.year_wise_revenue).length > 0 && (
            <>
              <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                Year-wise revenue
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {Object.entries(a.year_wise_revenue).map(([year, amt]) => (
                  <Chip key={year} label={`${year}: ${formatInr(amt)}`} />
                ))}
              </Stack>
            </>
          )}
        </SectionPanel>
      );

    case "actions":
      return (
        <SectionPanel title="Quick actions">
          <Grid container spacing={1}>
            {profile.quick_actions.map((action) => (
              <Grid key={action.code} size={{ xs: 6, sm: 4, md: 3 }}>
                <Button
                  component={action.href.startsWith("tel:") || action.href.startsWith("http") ? "a" : Link}
                  href={action.href}
                  variant="outlined"
                  fullWidth
                  sx={{ textTransform: "none", justifyContent: "flex-start", py: 1.25 }}
                >
                  {action.label}
                </Button>
              </Grid>
            ))}
          </Grid>
        </SectionPanel>
      );

    default:
      return null;
  }
}

export default function FarmerDetailPage() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const farmerId = params.id;
  const queryClient = useQueryClient();
  const [editOpen, setEditOpen] = useState(false);
  const [form, setForm] = useState<EditForm | null>(null);
  const initialTab = (searchParams.get("tab") as Farmer360Section | null) ?? "overview";
  const [section, setSection] = useState<Farmer360Section>(initialTab);

  useEffect(() => {
    const tab = searchParams.get("tab") as Farmer360Section | null;
    if (tab) setSection(tab);
  }, [searchParams]);

  const detailQuery = useQuery({
    queryKey: ["farmer", farmerId],
    queryFn: () => fetchFarmer(farmerId),
    enabled: Boolean(farmerId),
  });

  const profileQuery = useQuery({
    queryKey: ["farmer-360", farmerId],
    queryFn: () => fetchFarmer360(farmerId),
    enabled: Boolean(farmerId),
  });

  const saveMutation = useMutation({
    mutationFn: () => {
      if (!form) throw new Error("No form");
      return updateFarmer(farmerId, {
        full_name: form.fullName.trim(),
        full_name_te: form.fullNameTe.trim() || null,
        phone_primary: form.phone.trim(),
        phone_secondary: form.phoneSecondary.trim() || null,
        address: form.address.trim() || null,
        notes: form.notes.trim() || null,
        status: form.status,
        village_id: form.location.villageId,
        preferred_language: form.preferredLanguage.trim() || null,
        preferred_payment_cycle: form.preferredPaymentCycle.trim() || null,
        preferred_payment_method: form.preferredPaymentMethod.trim() || null,
        trust_rating: form.trustRating ? Number(form.trustRating) : null,
        is_vip: form.isVip,
      });
    },
    onSuccess: (updated) => {
      queryClient.setQueryData(["farmer", farmerId], updated);
      queryClient.invalidateQueries({ queryKey: ["farmers"] });
      queryClient.invalidateQueries({ queryKey: ["farmer-360", farmerId] });
      setEditOpen(false);
      setForm(null);
    },
  });

  const openEdit = () => {
    if (!detailQuery.data) return;
    setForm(formFromFarmer(detailQuery.data));
    saveMutation.reset();
    setEditOpen(true);
  };

  const canSave =
    Boolean(form) &&
    form!.fullName.trim().length >= 2 &&
    form!.phone.trim().length >= 10 &&
    Boolean(form!.location.villageId) &&
    !saveMutation.isPending;

  const profile = profileQuery.data;
  const summary = profile?.summary;
  const isLoading = detailQuery.isLoading || profileQuery.isLoading;
  const isError = detailQuery.isError || profileQuery.isError;
  const error = detailQuery.error || profileQuery.error;

  const headerChips = useMemo(() => {
    if (!summary) return [];
    const chips = [summary.status_label];
    if (summary.preferred_language) chips.push(summary.preferred_language.toUpperCase());
    if (summary.preferred_payment_cycle) chips.push(summary.preferred_payment_cycle);
    return chips;
  }, [summary]);

  return (
    <MuiPageShell
      title={summary?.full_name ?? detailQuery.data?.full_name ?? "Farmer 360°"}
      description={
        summary
          ? `${summary.farmer_code} · ${[summary.village_name, summary.mandal, summary.district].filter(Boolean).join(" · ") || "—"}`
          : "Loading relationship profile…"
      }
      actions={
        <Stack direction="row" spacing={1}>
          {detailQuery.data && (
            <Button variant="contained" startIcon={<EditOutlined />} onClick={openEdit}>
              Edit
            </Button>
          )}
          <Button component={Link} href="/farmers" startIcon={<ArrowBack />} variant="outlined">
            Back to list
          </Button>
        </Stack>
      }
    >
      {isLoading && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {isError && (
        <Alert severity="warning">
          {error instanceof Error ? error.message : "Could not load farmer 360 profile"}
        </Alert>
      )}

      {profile && summary && (
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
              <Farmer360Orbit
                farmerName={summary.full_name}
                farmerCode={summary.farmer_code}
                statusLabel={summary.status_label}
                trustRating={summary.trust_rating}
                active={section}
                onSelect={setSection}
              />

              <Stack spacing={1.25} sx={{ mt: 2.5 }}>
                <Typography variant="body2">
                  <strong>Mobile:</strong> {summary.phone_primary}
                  {summary.phone_secondary ? ` · ${summary.phone_secondary}` : ""}
                </Typography>
                <Typography variant="body2">
                  <strong>Address:</strong> {summary.address ?? "—"}
                </Typography>
                <Typography variant="body2">
                  <strong>Payment method:</strong> {summary.preferred_payment_method ?? "—"}
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {headerChips.map((chip) => (
                    <Chip key={chip} size="small" label={chip} color="primary" variant="outlined" />
                  ))}
                  {summary.trust_rating != null && (
                    <Chip
                      size="small"
                      icon={<Star sx={{ fontSize: 14 }} />}
                      label={`${summary.trust_rating}/5`}
                    />
                  )}
                  {summary.tags.map((tag) => (
                    <Chip key={tag} size="small" label={tag} />
                  ))}
                </Stack>
                <Typography variant="h5" color="primary.main" fontWeight={700}>
                  {formatInr(profile.statistics.outstanding_amount)}{" "}
                  <Typography component="span" variant="caption" color="text.secondary">
                    outstanding
                  </Typography>
                </Typography>
              </Stack>
            </Box>
          </Grid>

          <Grid size={{ xs: 12, lg: 7 }}>
            <Stack spacing={2}>{renderSection(section, profile, farmerId)}</Stack>
          </Grid>
        </Grid>
      )}

      <PremiumDialog
        open={editOpen && Boolean(form)}
        onClose={() => setEditOpen(false)}
        maxWidth="sm"
      >
        <PremiumDialogTitle>Edit farmer</PremiumDialogTitle>
        <PremiumDialogContent sx={{ overflow: "visible", pt: 0.5, pb: 2 }}>
          {form && (
            <Scope className="flex flex-col gap-5 bg-transparent">
              <PremiumField label="Full name" required>
                <Input
                  autoFocus
                  value={form.fullName}
                  onChange={(e) => setForm({ ...form, fullName: e.target.value })}
                />
              </PremiumField>
              <PremiumField label="Full name (Telugu)">
                <Input
                  value={form.fullNameTe}
                  onChange={(e) => setForm({ ...form, fullNameTe: e.target.value })}
                />
              </PremiumField>
              <PremiumField label="Primary phone" required>
                <Input
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                />
              </PremiumField>
              <PremiumField label="Secondary phone">
                <Input
                  value={form.phoneSecondary}
                  onChange={(e) => setForm({ ...form, phoneSecondary: e.target.value })}
                />
              </PremiumField>

              <LocationCascade
                required
                value={form.location}
                hydrateVillageId={detailQuery.data?.village_id}
                onChange={(location) =>
                  setForm((prev) => (prev ? { ...prev, location } : prev))
                }
              />

              <TextField
                select
                fullWidth
                label="Status"
                value={form.status}
                onChange={(e) => setForm({ ...form, status: e.target.value })}
                sx={{ "& .MuiInputBase-root": { minHeight: 52 } }}
              >
                <MenuItem value="active">Active</MenuItem>
                <MenuItem value="inactive">Inactive</MenuItem>
                <MenuItem value="blocked">Blacklisted</MenuItem>
              </TextField>

              <TextField
                select
                fullWidth
                label="VIP farmer"
                value={form.isVip ? "yes" : "no"}
                onChange={(e) => setForm({ ...form, isVip: e.target.value === "yes" })}
                sx={{ "& .MuiInputBase-root": { minHeight: 52 } }}
              >
                <MenuItem value="no">No</MenuItem>
                <MenuItem value="yes">Yes</MenuItem>
              </TextField>

              <TextField
                select
                fullWidth
                label="Trust rating"
                value={form.trustRating}
                onChange={(e) => setForm({ ...form, trustRating: e.target.value })}
                sx={{ "& .MuiInputBase-root": { minHeight: 52 } }}
              >
                <MenuItem value="">—</MenuItem>
                {[1, 2, 3, 4, 5].map((n) => (
                  <MenuItem key={n} value={String(n)}>
                    {n} star{n > 1 ? "s" : ""}
                  </MenuItem>
                ))}
              </TextField>

              <PremiumField label="Preferred language">
                <Input
                  value={form.preferredLanguage}
                  onChange={(e) => setForm({ ...form, preferredLanguage: e.target.value })}
                  placeholder="en / te"
                />
              </PremiumField>
              <PremiumField label="Preferred payment cycle">
                <Input
                  value={form.preferredPaymentCycle}
                  onChange={(e) => setForm({ ...form, preferredPaymentCycle: e.target.value })}
                />
              </PremiumField>
              <PremiumField label="Preferred payment method">
                <Input
                  value={form.preferredPaymentMethod}
                  onChange={(e) => setForm({ ...form, preferredPaymentMethod: e.target.value })}
                />
              </PremiumField>

              <PremiumField label="Address">
                <Input
                  value={form.address}
                  onChange={(e) => setForm({ ...form, address: e.target.value })}
                />
              </PremiumField>
              <PremiumField label="Notes">
                <Input
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                />
              </PremiumField>

              {saveMutation.isError && (
                <SoftAlert severity="error">
                  {saveMutation.error instanceof Error
                    ? saveMutation.error.message
                    : "Save failed"}
                </SoftAlert>
              )}
            </Scope>
          )}
        </PremiumDialogContent>
        <PremiumDialogActions className={PREMIUM_SCOPE}>
          <PremiumButton variant="secondary" size="sm" onClick={() => setEditOpen(false)}>
            Cancel
          </PremiumButton>
          <PremiumButton
            variant="primary"
            size="sm"
            disabled={!canSave}
            onClick={() => saveMutation.mutate()}
          >
            {saveMutation.isPending ? "Saving…" : "Save"}
          </PremiumButton>
        </PremiumDialogActions>
      </PremiumDialog>
    </MuiPageShell>
  );
}
