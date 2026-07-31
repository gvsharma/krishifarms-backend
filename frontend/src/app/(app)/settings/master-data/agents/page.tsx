"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import { createAgent, deleteAgent, fetchAgents, updateAgent } from "@/features/master-data/api";

export default function AgentsPage() {
  return (
    <CatalogAdminPage
      title="Field agents"
      description="Collection and village agent roster."
      queryKey="agents-admin"
      fields={[
        { key: "name", label: "Name", required: true },
        { key: "name_te", label: "Name (Telugu)", table: false },
        { key: "phone", label: "Phone", type: "phone" },
        { key: "commission_pct", label: "Commission %", type: "number" },
        { key: "notes", label: "Notes", table: false },
        { key: "is_active", label: "Active", type: "boolean" },
      ]}
      list={() => fetchAgents(1, 100)}
      create={createAgent}
      update={updateAgent}
      remove={deleteAgent}
      rowLabel={(r) => r.name}
    />
  );
}
