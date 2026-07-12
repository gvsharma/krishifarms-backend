"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import { SERVICE_CATEGORIES } from "@/features/field-services/constants";
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
      description="Service / labour activity catalog for work orders and field services."
      queryKey="activity-types-admin"
      fields={[
        {
          key: "name",
          label: "Name",
          required: true,
          placeholder: "e.g. Cultivator Work, Fertilizer Pump Work",
        },
        { key: "code", label: "Code", required: true, createOnly: true },
        { key: "name_te", label: "Name (Telugu)", table: false },
        {
          key: "service_category",
          label: "Service category",
          type: "select",
          options: SERVICE_CATEGORIES.map((cat) => ({ value: cat.value, label: cat.label })),
        },
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
