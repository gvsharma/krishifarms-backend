"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import {
  createActivityType,
  deleteActivityType,
  fetchActivityTypes,
  updateActivityType,
} from "@/features/master-data/api";

export default function ActivityTypesPage() {
  return (
    <CatalogAdminPage
      title="Activity types"
      description="Service / labour activity catalog for work orders."
      queryKey="activity-types-admin"
      fields={[
        { key: "name", label: "Name", required: true },
        { key: "code", label: "Code", required: true, createOnly: true },
        { key: "name_te", label: "Name (Telugu)", table: false },
        {
          key: "default_rate_type",
          label: "Default rate type",
          type: "select",
          options: [
            { value: "hourly", label: "Hourly" },
            { value: "daily", label: "Daily" },
            { value: "fixed", label: "Fixed" },
          ],
        },
        { key: "is_active", label: "Active", type: "boolean" },
      ]}
      list={() => fetchActivityTypes(1, 100)}
      create={createActivityType}
      update={updateActivityType}
      remove={deleteActivityType}
      rowLabel={(r) => r.name}
    />
  );
}
