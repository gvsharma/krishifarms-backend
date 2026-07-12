"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import { createBuyer, deleteBuyer, fetchBuyers, updateBuyer } from "@/features/master-data/api";
import { useTranslations } from "@/i18n/use-translations";

export default function BuyersPage() {
  const { t } = useTranslations();

  return (
    <CatalogAdminPage
      title={t("catalog.buyers")}
      description={t("catalog.buyersDesc")}
      queryKey="buyers-admin"
      fields={[
        { key: "name", label: t("catalog.fields.name"), required: true },
        { key: "name_te", label: t("catalog.fields.nameTe"), table: false },
        { key: "phone", label: t("catalog.fields.phone") },
        { key: "gstin", label: t("catalog.fields.gstin"), table: false },
        { key: "contact_person", label: t("catalog.fields.contactPerson") },
        { key: "address", label: t("catalog.fields.address"), table: false },
        { key: "notes", label: t("common.notes"), table: false },
        { key: "is_active", label: t("common.active"), type: "boolean" },
      ]}
      list={() => fetchBuyers(1, 100)}
      create={createBuyer}
      update={updateBuyer}
      remove={deleteBuyer}
      rowLabel={(r) => r.name}
    />
  );
}
