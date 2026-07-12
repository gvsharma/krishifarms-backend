"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import { FLEET_INVENTORY_SUMMARY, FUEL_TYPE_OPTIONS } from "@/constants/fleet-inventory";
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
      description={`KrishiFarms fleet — ${FLEET_INVENTORY_SUMMARY}.`}
      queryKey="vehicle-types-admin"
      fields={[
        {
          key: "name",
          label: "Name",
          required: true,
          placeholder: "e.g. Tractor, John Deere tractor 2W, Fertilizer Pump",
        },
        {
          key: "code",
          label: "Code",
          required: true,
          createOnly: true,
          placeholder: "e.g. TRACTOR, JD_TRACTOR_2W, FERTILIZER_PUMP",
        },
        { key: "name_te", label: "Name (Telugu)", table: false },
        { key: "capacity_quintals", label: "Capacity (qtl)", type: "number" },
        {
          key: "fuel_type",
          label: "Fuel type",
          type: "select",
          options: FUEL_TYPE_OPTIONS.map((opt) => ({ value: opt.value, label: opt.label })),
        },
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
