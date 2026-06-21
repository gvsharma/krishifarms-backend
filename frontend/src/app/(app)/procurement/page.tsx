import { Wheat } from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";

export const metadata = { title: "Procurement" };

export default function ProcurementPage() {
  return (
    <PlaceholderPage
      title="Procurement"
      description="Procurement board, dispatch tracking, and confirmation workflow."
      icon={Wheat}
    />
  );
}
