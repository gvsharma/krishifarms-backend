"use client";

import { CatalogAdminPage } from "@/components/admin/catalog-admin-page";
import {
  createExpenseCategory,
  deleteExpenseCategory,
  fetchExpenseCategories,
  updateExpenseCategory,
} from "@/features/master-data/api";

export default function ExpenseCategoriesPage() {
  return (
    <CatalogAdminPage
      title="Expense categories"
      description="Categories for operational expenses (fuel, labour, repairs, etc.)."
      queryKey="expense-categories-admin"
      fields={[
        { key: "name", label: "Name", required: true },
        { key: "name_te", label: "Name (Telugu)", table: false },
        {
          key: "type",
          label: "Type",
          type: "select",
          required: true,
          options: [
            { value: "expense", label: "Expense" },
            { value: "income", label: "Income" },
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
