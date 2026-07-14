"use client";

import { Alert, Box } from "@mui/material";
import dynamic from "next/dynamic";
import { useParams } from "next/navigation";
import type { ComponentType } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { ALL_MODULE_IDS } from "@/features/analytics/types";

const ExecutiveModule = dynamic(
  () => import("@/features/analytics/modules/executive").then((m) => m.ExecutiveModule),
  { ssr: false, loading: () => <Box sx={{ py: 4 }}>Loading module…</Box> },
);
const OperationsModule = dynamic(
  () => import("@/features/analytics/modules/operations").then((m) => m.OperationsModule),
  { ssr: false },
);
const ProcurementModule = dynamic(
  () => import("@/features/analytics/modules/procurement").then((m) => m.ProcurementModule),
  { ssr: false },
);
const FinanceModule = dynamic(
  () => import("@/features/analytics/modules/finance").then((m) => m.FinanceModule),
  { ssr: false },
);
const ScaffoldModule = dynamic(
  () => import("@/features/analytics/modules/_scaffold").then((m) => m.ScaffoldModule),
  { ssr: false },
);

const LIVE_RENDERERS: Record<string, ComponentType> = {
  executive: ExecutiveModule,
  operations: OperationsModule,
  procurement: ProcurementModule,
  finance: FinanceModule,
};

export default function AnalyticsModulePage() {
  const params = useParams<{ module: string }>();
  const moduleId = params.module;

  if (!ALL_MODULE_IDS.includes(moduleId as (typeof ALL_MODULE_IDS)[number])) {
    return (
      <MuiPageShell title="Analytics">
        <Alert severity="warning">Unknown analytics module: {moduleId}</Alert>
      </MuiPageShell>
    );
  }

  const Live = LIVE_RENDERERS[moduleId];
  return (
    <MuiPageShell title="Analytics" description={`Module: ${moduleId}`}>
      {Live ? <Live /> : <ScaffoldModule moduleId={moduleId} />}
    </MuiPageShell>
  );
}
