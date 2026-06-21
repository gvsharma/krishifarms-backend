import { Sprout } from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";

export const metadata = { title: "Farms" };

export default function FarmsPage() {
  return (
    <PlaceholderPage
      title="Farms"
      description="Land parcels, crop history, and acreage across villages."
      icon={Sprout}
    />
  );
}
