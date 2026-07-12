"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import {
  createActivityType,
  deleteActivityType,
  fetchActivityTypes,
  updateActivityType,
} from "@/features/master-data/api";
import { useTranslations } from "@/i18n/use-translations";

export default function ActivityTypesPage() {
  const { t } = useTranslations();

  return (
    <CatalogAdminPage
      title={t("catalog.activityTypes")}
      description={t("catalog.activityTypesDesc")}
      queryKey="activity-types-admin"
      fields={[
        { key: "name", label: t("catalog.fields.name"), required: true },
        { key: "code", label: t("catalog.fields.code"), required: true, createOnly: true },
        { key: "name_te", label: t("catalog.fields.nameTe"), table: false },
        {
          key: "default_rate_type",
          label: t("catalog.fields.defaultRateType"),
          type: "select",
          options: [
            { value: "hourly", label: t("catalog.fields.hourly") },
            { value: "daily", label: t("catalog.fields.daily") },
            { value: "fixed", label: t("catalog.fields.fixed") },
          ],
        },
        { key: "is_active", label: t("common.active"), type: "boolean" },
      ]}
      list={() => fetchActivityTypes(1, 100)}
      create={createActivityType}
      update={updateActivityType}
      remove={deleteActivityType}
      rowLabel={(r) => r.name}
    />
  );
}
