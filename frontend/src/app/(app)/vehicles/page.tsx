import { Truck } from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";

export const metadata = { title: "Vehicles" };

export default function VehiclesPage() {
  return (
    <PlaceholderPage
      title="Vehicles"
      description="Fleet assets, trips, fuel efficiency, and maintenance."
      icon={Truck}
    />
  );
}
