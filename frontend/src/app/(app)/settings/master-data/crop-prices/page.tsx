"use client";

import { useQuery } from "@tanstack/react-query";
import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import {
  createCropPrice,
  deleteCropPrice,
  fetchCropPrices,
  fetchCropTypes,
  updateCropPrice,
} from "@/features/master-data/api";

export default function CropPricesPage() {
  const cropsQuery = useQuery({
    queryKey: ["crop-types-lookup"],
    queryFn: () => fetchCropTypes(1, 100),
  });

  const cropOptions =
    cropsQuery.data?.items.map((c) => ({ value: c.id, label: `${c.name} (${c.code})` })) ?? [];

  return (
    <CatalogAdminPage
      title="Crop price rules"
      description="Effective rates per quintal used when pricing procurements."
      queryKey="crop-prices-admin"
      fields={[
        {
          key: "crop_type_id",
          label: "Crop type",
          type: "select",
          required: true,
          createOnly: true,
          options: cropOptions,
        },
        { key: "effective_from", label: "Effective from", type: "date", required: true },
        { key: "effective_to", label: "Effective to", type: "date" },
        { key: "rate_per_quintal", label: "Rate / quintal (₹)", type: "number", required: true },
        { key: "notes", label: "Notes", table: false },
        { key: "is_active", label: "Active", type: "boolean" },
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
