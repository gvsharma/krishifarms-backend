import { Settings } from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";

export const metadata = { title: "Settings" };

export default function SettingsPage() {
  return (
    <PlaceholderPage
      title="Settings"
      description="Organization, users, roles, appearance, and locale preferences."
      icon={Settings}
    />
  );
}
