import { Receipt } from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";

export const metadata = { title: "Expenses" };

export default function ExpensesPage() {
  return (
    <PlaceholderPage
      title="Expenses"
      description="Operational expenses, categories, and approval workflow."
      icon={Receipt}
    />
  );
}
