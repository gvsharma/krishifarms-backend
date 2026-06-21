import { CreditCard } from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";

export const metadata = { title: "Payments" };

export default function PaymentsPage() {
  return (
    <PlaceholderPage
      title="Payments"
      description="Farmer payments, allocation, and settlement queue."
      icon={CreditCard}
    />
  );
}
