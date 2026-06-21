import { Tractor } from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";

export const metadata = { title: "Workers" };

export default function WorkersPage() {
  return (
    <PlaceholderPage
      title="Workers"
      description="Workforce roster, attendance, and wage tracking."
      icon={Tractor}
    />
  );
}
