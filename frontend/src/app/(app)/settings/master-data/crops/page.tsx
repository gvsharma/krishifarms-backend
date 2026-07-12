"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import {
  createCropType,
  deleteCropType,
  fetchCropTypes,
  updateCropType,
} from "@/features/master-data/api";
import { useTranslations } from "@/i18n/use-translations";

export default function CropTypesPage() {
  const { t } = useTranslations();

  return (
    <CatalogAdminPage
      title={t("catalog.cropTypes")}
      description={t("catalog.cropTypesDesc")}
      queryKey="crop-types-admin"
      fields={[
        { key: "name", label: t("catalog.fields.name"), required: true },
        { key: "code", label: t("catalog.fields.code"), required: true, createOnly: true },
        { key: "default_moisture_pct", label: t("catalog.fields.defaultMoisturePct"), type: "number" },
        { key: "is_active", label: t("common.active"), type: "boolean" },
      ]}
      list={() => fetchCropTypes(1, 100)}
      create={(p) => createCropType(p as { name: string; code: string })}
      update={(id, p) => updateCropType(id, p)}
      remove={deleteCropType}
      rowLabel={(r) => r.name}
    />
  );
}
