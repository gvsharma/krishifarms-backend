"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import {
  createVehicleType,
  deleteVehicleType,
  fetchVehicleTypes,
  updateVehicleType,
} from "@/features/master-data/api";

export default function VehicleTypesPage() {
  return (
    <CatalogAdminPage
      title="Vehicle types"
      description="Fleet categories (tractor, tipper, etc.) shared with mobile."
      queryKey="vehicle-types-admin"
      fields={[
        { key: "name", label: "Name", required: true },
        { key: "code", label: "Code", required: true, createOnly: true },
        { key: "name_te", label: "Name (Telugu)", table: false },
        { key: "capacity_quintals", label: "Capacity (qtl)", type: "number" },
        { key: "fuel_type", label: "Fuel type" },
        { key: "notes", label: "Notes", table: false },
        { key: "is_active", label: "Active", type: "boolean" },
      ]}
      list={() => fetchVehicleTypes(1, 100)}
      create={createVehicleType}
      update={updateVehicleType}
      remove={deleteVehicleType}
      rowLabel={(r) => r.name}
    />
  );
}
