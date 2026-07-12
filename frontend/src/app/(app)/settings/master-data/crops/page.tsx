"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import {
  createCropType,
  deleteCropType,
  fetchCropTypes,
  updateCropType,
} from "@/features/master-data/api";

export default function CropTypesPage() {
  return (
    <CatalogAdminPage
      title="Crop types"
      description="Paddy, Corn, Maize, Cotton, grams, oilseeds, Vegetables, Others — used by procurement and tractor work."
      queryKey="crop-types-admin"
      fields={[
        { key: "name", label: "Name", required: true },
        { key: "code", label: "Code", required: true, createOnly: true },
        { key: "default_moisture_pct", label: "Default moisture %", type: "number" },
        { key: "is_active", label: "Active", type: "boolean" },
      ]}
      list={() => fetchCropTypes(1, 100)}
      create={(p) => createCropType(p as { name: string; code: string })}
      update={(id, p) => updateCropType(id, p)}
      remove={deleteCropType}
      rowLabel={(r) => r.name}
    />
  );
}
