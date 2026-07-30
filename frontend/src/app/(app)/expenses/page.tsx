"use client";

import { Receipt } from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";

export default function ExpensesPage() {
  return (
    <PlaceholderPage
      titleKey="pages.expenses"
      descriptionKey="pages.expensesDesc"
      icon={Receipt}
    />
  );
}
