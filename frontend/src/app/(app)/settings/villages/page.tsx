"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import {
  createVillage,
  deleteVillage,
  fetchVillages,
  updateVillage,
} from "@/features/master-data/api";

export default function SettingsVillagesPage() {
  return (
    <CatalogAdminPage
      title="Villages"
      description="Geography master for farmers, agents, and procurements."
      queryKey="villages"
      fields={[
        { key: "name", label: "Name", required: true },
        { key: "mandal", label: "Mandal" },
        { key: "district", label: "District" },
        { key: "state", label: "State" },
        { key: "pincode", label: "Pincode", table: false },
      ]}
      list={() => fetchVillages(1, 100)}
      create={(p) => createVillage(p as { name: string })}
      update={(id, p) => updateVillage(id, p)}
      remove={deleteVillage}
      rowLabel={(r) => r.name}
    />
  );
}
