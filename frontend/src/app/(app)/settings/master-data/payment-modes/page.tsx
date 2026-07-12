"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import {
  createPaymentMode,
  deletePaymentMode,
  fetchPaymentModes,
  updatePaymentMode,
} from "@/features/master-data/api";
import { useTranslations } from "@/i18n/use-translations";

export default function PaymentModesPage() {
  const { t } = useTranslations();

  return (
    <CatalogAdminPage
      title={t("catalog.paymentModes")}
      description={t("catalog.paymentModesDesc")}
      queryKey="payment-modes-admin"
      fields={[
        { key: "name", label: t("catalog.fields.name"), required: true },
        { key: "code", label: t("catalog.fields.code"), required: true, createOnly: true },
        { key: "name_te", label: t("catalog.fields.nameTe"), table: false },
        { key: "is_active", label: t("common.active"), type: "boolean" },
      ]}
      list={() => fetchPaymentModes(1, 100)}
      create={createPaymentMode}
      update={updatePaymentMode}
      remove={deletePaymentMode}
      rowLabel={(r) => r.name}
    />
  );
}
