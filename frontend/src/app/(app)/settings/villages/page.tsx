"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import {
  createVillage,
  deleteVillage,
  fetchVillages,
  updateVillage,
} from "@/features/master-data/api";
import { useTranslations } from "@/i18n/use-translations";

export default function SettingsVillagesPage() {
  const { t } = useTranslations();

  return (
    <CatalogAdminPage
      title={t("catalog.villages")}
      description={t("catalog.villagesDesc")}
      queryKey="villages"
      fields={[
        { key: "name", label: t("catalog.fields.name"), required: true },
        { key: "mandal", label: t("catalog.fields.mandal") },
        { key: "district", label: t("catalog.fields.district") },
        { key: "state", label: t("catalog.fields.state") },
        { key: "pincode", label: t("catalog.fields.pincode"), table: false },
      ]}
      list={() => fetchVillages(1, 100)}
      create={(p) => createVillage(p as { name: string })}
      update={(id, p) => updateVillage(id, p)}
      remove={deleteVillage}
      rowLabel={(r) => r.name}
    />
  );
}
