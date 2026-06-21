import { Users } from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";

export const metadata = { title: "Farmers" };

export default function FarmersPage() {
  return (
    <PlaceholderPage
      title="Farmers"
      description="Manage farmer profiles, outstanding balances, and village assignments."
      icon={Users}
    />
  );
}
