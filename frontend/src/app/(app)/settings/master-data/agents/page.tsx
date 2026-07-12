"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import { createAgent, deleteAgent, fetchAgents, updateAgent } from "@/features/master-data/api";
import { useTranslations } from "@/i18n/use-translations";

export default function AgentsPage() {
  const { t } = useTranslations();

  return (
    <CatalogAdminPage
      title={t("catalog.agents")}
      description={t("catalog.agentsDesc")}
      queryKey="agents-admin"
      fields={[
        { key: "name", label: t("catalog.fields.name"), required: true },
        { key: "name_te", label: t("catalog.fields.nameTe"), table: false },
        { key: "phone", label: t("catalog.fields.phone") },
        { key: "commission_pct", label: t("catalog.fields.commissionPct"), type: "number" },
        { key: "notes", label: t("common.notes"), table: false },
        { key: "is_active", label: t("common.active"), type: "boolean" },
      ]}
      list={() => fetchAgents(1, 100)}
      create={createAgent}
      update={updateAgent}
      remove={deleteAgent}
      rowLabel={(r) => r.name}
    />
  );
}
