"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import {
  createCropPrice,
  deleteCropPrice,
  fetchCropPrices,
  fetchCropTypes,
  updateCropPrice,
} from "@/features/master-data/api";
import { useTranslations } from "@/i18n/use-translations";

export default function CropPricesPage() {
  const { t } = useTranslations();
  const cropsQuery = useQuery({
    queryKey: ["crop-types-lookup"],
    queryFn: () => fetchCropTypes(1, 100),
  });

  const cropNameById = useMemo(() => {
    const map = new Map<string, string>();
    for (const crop of cropsQuery.data?.items ?? []) {
      map.set(crop.id, crop.name);
    }
    return map;
  }, [cropsQuery.data?.items]);

  const cropOptions = cropsQuery.data?.items.map((c) => ({ value: c.id, label: c.name })) ?? [];

  return (
    <CatalogAdminPage
      title={t("catalog.cropPrices")}
      description={t("catalog.cropPricesDesc")}
      queryKey="crop-prices-admin"
      fields={[
        {
          key: "crop_type_id",
          label: t("catalog.fields.cropType"),
          type: "select",
          required: true,
          createOnly: true,
          options: cropOptions,
          formatTable: (value) => cropNameById.get(String(value)) ?? t("common.dash"),
        },
        { key: "effective_from", label: t("catalog.fields.effectiveFrom"), type: "date", required: true },
        { key: "effective_to", label: t("catalog.fields.effectiveTo"), type: "date" },
        { key: "rate_per_quintal", label: t("catalog.fields.ratePerQuintal"), type: "number", required: true },
        { key: "notes", label: t("common.notes"), table: false },
        { key: "is_active", label: t("common.active"), type: "boolean" },
      ]}
      list={() => fetchCropPrices(1, 100)}
      create={createCropPrice}
      update={updateCropPrice}
      remove={deleteCropPrice}
      rowLabel={(r) => `₹${r.rate_per_quintal}`}
      toFormValues={(row) => ({
        crop_type_id: row.crop_type_id,
        effective_from: row.effective_from,
        effective_to: row.effective_to ?? "",
        rate_per_quintal: row.rate_per_quintal,
        notes: row.notes ?? "",
        is_active: row.is_active,
      })}
    />
  );
}
