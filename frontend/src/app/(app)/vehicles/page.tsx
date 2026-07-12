import { Truck } from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";
import { FLEET_INVENTORY_SUMMARY } from "@/constants/fleet-inventory";

export const metadata = { title: "Vehicles" };

export default function VehiclesPage() {
  return (
    <PlaceholderPage
      title="Vehicles"
      description={`Fleet assets — ${FLEET_INVENTORY_SUMMARY}. Trips, fuel, and maintenance coming soon.`}
      icon={Truck}
    />
  );
}
