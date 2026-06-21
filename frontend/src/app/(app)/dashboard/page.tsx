import {
  Activity,
  ArrowUpRight,
  Banknote,
  CircleDollarSign,
  Landmark,
  MapPin,
  Scale,
  Sprout,
  TrendingUp,
  Users,
} from "lucide-react";
import { KpiCard } from "@/components/kpi/kpi-card";
import { PageShell } from "@/components/shell/page-shell";
import { Button } from "@/components/ui/button";
import { formatCompact, formatCurrency } from "@/lib/utils";

export const metadata = {
  title: "Dashboard",
};

const RECENT_ACTIVITY = [
  {
    id: "1",
    text: "PR-2026-0142 confirmed · Rajesh Kumar · 45 qtl Paddy",
    time: "10 min ago",
    type: "procurement",
  },
  {
    id: "2",
    text: "FP-2026-0088 completed · ₹50,000 advance payment",
    time: "1 hr ago",
    type: "payment",
  },
  {
    id: "3",
    text: "Collection trip T-442 dispatched · Bhairkhanpally → Mill",
    time: "2 hr ago",
    type: "trip",
  },
  {
    id: "4",
    text: "New farmer registered · Lakshmi Devi · Yellareddypet",
    time: "3 hr ago",
    type: "farmer",
  },
];

const TOP_VILLAGES = [
  { name: "Bhairkhanpally", nameTe: "భైర్ఖాన్‌పల్లి", farmers: 68, volume: "4,820 qtl" },
  { name: "Yellareddypet", nameTe: "యెల్లారెడ్డిపేట", farmers: 42, volume: "2,940 qtl" },
  { name: "Kondapur", nameTe: "కొండాపూర్", farmers: 31, volume: "1,650 qtl" },
  { name: "Ramannapet", nameTe: "రామన్నపేట", farmers: 24, volume: "980 qtl" },
];

export default function DashboardPage() {
  return (
    <PageShell
      title="Executive Dashboard"
      description="Farm operations overview for Bhairkhanpally season — procurement, collections, and cash position."
      actions={
        <>
          <Button variant="outline" size="sm" className="rounded-xl">
            Jun 2026
          </Button>
          <Button variant="outline" size="sm" className="rounded-xl">
            All villages
          </Button>
        </>
      }
    >
      {/* Hero metric */}
      <section className="mb-6 surface-card overflow-hidden p-6 sm:p-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-muted-foreground">
              Net cash position
            </p>
            <p className="mt-2 font-display text-4xl font-semibold tabular-nums tracking-tight text-foreground sm:text-5xl">
              {formatCurrency(845230)}
            </p>
            <p className="mt-2 inline-flex items-center gap-1.5 text-sm text-success">
              <TrendingUp className="h-4 w-4" />
              <span className="font-medium">+12.4%</span>
              <span className="text-muted-foreground">vs last month</span>
            </p>
          </div>
          <div className="chart-placeholder relative h-24 w-full rounded-xl lg:h-28 lg:w-80">
            <div className="absolute inset-x-0 bottom-0 flex h-full items-end gap-1 px-4 pb-3">
              {[40, 55, 45, 60, 52, 70, 65, 80, 75, 90, 85, 95].map((h, i) => (
                <div
                  key={i}
                  className="flex-1 rounded-t-sm bg-primary/30"
                  style={{ height: `${h}%` }}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* KPI grid */}
      <section className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard
          label="Total Farmers"
          value="142"
          delta={4.2}
          icon={Users}
          delay={0}
        />
        <KpiCard
          label="Acreage"
          value="486 ac"
          delta={1.8}
          icon={Sprout}
          iconClassName="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
          delay={50}
        />
        <KpiCard
          label="Today's Collections"
          value="128 qtl"
          delta={8.5}
          icon={Scale}
          iconClassName="bg-harvest/10 text-harvest"
          delay={100}
        />
        <KpiCard
          label="Pending Payments"
          value={formatCurrency(410000)}
          delta={-3.2}
          icon={Banknote}
          iconClassName="bg-warning/10 text-warning"
          delay={150}
        />
        <KpiCard
          label="Procurement Volume"
          value="12,450 qtl"
          delta={5.1}
          icon={Landmark}
          delay={200}
        />
        <KpiCard
          label="Revenue"
          value={formatCompact(3240000)}
          delta={3.4}
          icon={CircleDollarSign}
          delay={250}
        />
        <KpiCard
          label="Expenses"
          value={formatCompact(2180000)}
          delta={2.1}
          icon={Activity}
          iconClassName="bg-muted text-muted-foreground"
          delay={300}
        />
        <KpiCard
          label="Profit"
          value={formatCompact(1060000)}
          delta={6.8}
          icon={TrendingUp}
          iconClassName="bg-success/10 text-success"
          delay={350}
        />
      </section>

      {/* Charts row */}
      <section className="mb-6 grid gap-4 lg:grid-cols-5">
        <div className="surface-card p-6 lg:col-span-3">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="font-display text-base font-semibold">Cash in vs out</h2>
              <p className="text-xs text-muted-foreground">Collections and procurement COGS — 30 days</p>
            </div>
            <Button variant="ghost" size="sm">
              View report <ArrowUpRight className="h-3.5 w-3.5" />
            </Button>
          </div>
          <div className="chart-placeholder h-56 rounded-xl">
            <div className="flex h-full items-end gap-2 px-4 pb-4 pt-8">
              {Array.from({ length: 12 }).map((_, i) => (
                <div key={i} className="flex flex-1 flex-col items-center gap-1">
                  <div
                    className="w-full rounded-t-md bg-primary/40"
                    style={{ height: `${30 + Math.sin(i) * 20 + 40}%` }}
                  />
                  <div
                    className="w-full rounded-t-md bg-harvest/30"
                    style={{ height: `${20 + Math.cos(i) * 15 + 25}%` }}
                  />
                </div>
              ))}
            </div>
          </div>
          <div className="mt-3 flex gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-primary/60" /> Collections
            </span>
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-harvest/60" /> Procurement COGS
            </span>
          </div>
        </div>

        <div className="surface-card p-6 lg:col-span-2">
          <h2 className="font-display text-base font-semibold">Crop mix</h2>
          <p className="mb-4 text-xs text-muted-foreground">Procurement by crop type</p>
          <div className="flex flex-col items-center gap-4 sm:flex-row">
            <div className="relative h-36 w-36 shrink-0">
              <svg viewBox="0 0 36 36" className="h-full w-full -rotate-90">
                <circle cx="18" cy="18" r="15.9" fill="none" stroke="hsl(var(--muted))" strokeWidth="3" />
                <circle
                  cx="18"
                  cy="18"
                  r="15.9"
                  fill="none"
                  stroke="hsl(var(--primary))"
                  strokeWidth="3"
                  strokeDasharray="68 100"
                  strokeLinecap="round"
                />
                <circle
                  cx="18"
                  cy="18"
                  r="15.9"
                  fill="none"
                  stroke="hsl(var(--harvest))"
                  strokeWidth="3"
                  strokeDasharray="32 100"
                  strokeDashoffset="-68"
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-lg font-semibold tabular-nums">12.4k</span>
                <span className="text-[10px] text-muted-foreground">qtl total</span>
              </div>
            </div>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-primary" />
                Paddy <span className="ml-auto font-medium tabular-nums">68%</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-harvest" />
                Corn <span className="ml-auto font-medium tabular-nums">32%</span>
              </li>
            </ul>
          </div>
        </div>
      </section>

      {/* Activity + villages */}
      <section className="grid gap-4 lg:grid-cols-2">
        <div className="surface-card p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-base font-semibold">Recent activity</h2>
            <Button variant="ghost" size="sm">
              View all
            </Button>
          </div>
          <ul className="space-y-4">
            {RECENT_ACTIVITY.map((item) => (
              <li key={item.id} className="flex gap-3">
                <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-primary" />
                <div className="min-w-0 flex-1">
                  <p className="text-sm text-foreground">{item.text}</p>
                  <p className="mt-0.5 text-xs text-muted-foreground">{item.time}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="surface-card p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-base font-semibold">Top villages</h2>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </div>
          <ul className="space-y-3">
            {TOP_VILLAGES.map((village, i) => (
              <li
                key={village.name}
                className="flex items-center gap-3 rounded-xl border border-border/50 bg-muted/20 px-4 py-3"
              >
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-xs font-semibold text-primary">
                  {i + 1}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium">{village.name}</p>
                  <p className="truncate font-telugu text-xs text-muted-foreground">{village.nameTe}</p>
                </div>
                <div className="text-right text-xs">
                  <p className="font-medium tabular-nums">{village.farmers} farmers</p>
                  <p className="text-muted-foreground">{village.volume}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </PageShell>
  );
}
