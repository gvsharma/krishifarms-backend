"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import {
  createPaymentMode,
  deletePaymentMode,
  fetchPaymentModes,
  updatePaymentMode,
} from "@/features/master-data/api";

export default function PaymentModesPage() {
  return (
    <CatalogAdminPage
      title="Payment modes"
      description="Cash, UPI, bank transfer, and other settlement modes."
      queryKey="payment-modes-admin"
      fields={[
        { key: "name", label: "Name", required: true },
        { key: "code", label: "Code", required: true, createOnly: true },
        { key: "name_te", label: "Name (Telugu)", table: false },
        { key: "is_active", label: "Active", type: "boolean" },
      ]}
      list={() => fetchPaymentModes(1, 100)}
      create={createPaymentMode}
      update={updatePaymentMode}
      remove={deletePaymentMode}
      rowLabel={(r) => r.name}
    />
  );
}
