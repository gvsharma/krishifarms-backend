"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import { createBuyer, deleteBuyer, fetchBuyers, updateBuyer } from "@/features/master-data/api";

export default function BuyersPage() {
  return (
    <CatalogAdminPage
      title="Buyers"
      description="Mills and traders used in procurement sales."
      queryKey="buyers-admin"
      fields={[
        { key: "name", label: "Name", required: true },
        { key: "name_te", label: "Name (Telugu)", table: false },
        { key: "phone", label: "Phone" },
        { key: "gstin", label: "GSTIN", table: false },
        { key: "contact_person", label: "Contact person" },
        { key: "address", label: "Address", table: false },
        { key: "notes", label: "Notes", table: false },
        { key: "is_active", label: "Active", type: "boolean" },
      ]}
      list={() => fetchBuyers(1, 100)}
      create={createBuyer}
      update={updateBuyer}
      remove={deleteBuyer}
      rowLabel={(r) => r.name}
    />
  );
}
