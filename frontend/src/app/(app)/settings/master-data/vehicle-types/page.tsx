"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import {
  createVehicleType,
  deleteVehicleType,
  fetchVehicleTypes,
  updateVehicleType,
} from "@/features/master-data/api";
import { useTranslations } from "@/i18n/use-translations";

export default function VehicleTypesPage() {
  const { t } = useTranslations();

  return (
    <CatalogAdminPage
      title={t("catalog.vehicleTypes")}
      description={t("catalog.vehicleTypesDesc")}
      queryKey="vehicle-types-admin"
      fields={[
        { key: "name", label: t("catalog.fields.name"), required: true },
        { key: "code", label: t("catalog.fields.code"), required: true, createOnly: true },
        { key: "name_te", label: t("catalog.fields.nameTe"), table: false },
        { key: "capacity_quintals", label: t("catalog.fields.capacityQuintals"), type: "number" },
        { key: "fuel_type", label: t("catalog.fields.fuelType") },
        { key: "notes", label: t("common.notes"), table: false },
        { key: "is_active", label: t("common.active"), type: "boolean" },
      ]}
      list={() => fetchVehicleTypes(1, 100)}
      create={createVehicleType}
      update={updateVehicleType}
      remove={deleteVehicleType}
      rowLabel={(r) => r.name}
    />
  );
}
