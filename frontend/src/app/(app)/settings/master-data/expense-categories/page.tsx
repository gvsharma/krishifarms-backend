"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import {
  createExpenseCategory,
  deleteExpenseCategory,
  fetchExpenseCategories,
  updateExpenseCategory,
} from "@/features/master-data/api";
import { useTranslations } from "@/i18n/use-translations";

export default function ExpenseCategoriesPage() {
  const { t } = useTranslations();

  return (
    <CatalogAdminPage
      title={t("catalog.expenseCategories")}
      description={t("catalog.expenseCategoriesDesc")}
      queryKey="expense-categories-admin"
      fields={[
        { key: "name", label: t("catalog.fields.name"), required: true },
        {
          key: "type",
          label: t("common.type"),
          type: "select",
          required: true,
          options: [
            { value: "expense", label: t("catalog.fields.expense") },
            { value: "income", label: t("catalog.fields.income") },
          ],
        },
      ]}
      list={() => fetchExpenseCategories(1, 100)}
      create={(p) => createExpenseCategory(p as { name: string; type?: string })}
      update={(id, p) => updateExpenseCategory(id, p)}
      remove={deleteExpenseCategory}
      rowLabel={(r) => r.name}
    />
  );
}
