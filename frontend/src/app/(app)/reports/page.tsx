import { BarChart3 } from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";

export const metadata = { title: "Reports" };

export default function ReportsPage() {
  return (
    <PlaceholderPage
      title="Reports"
      description="Executive reports, P&L, and village-level analytics."
      icon={BarChart3}
    />
  );
}
