import { Wallet } from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";

export const metadata = { title: "Collections" };

export default function CollectionsPage() {
  return (
    <PlaceholderPage
      title="Collections"
      description="Daily collection entries, weighment, and quality checks."
      icon={Wallet}
    />
  );
}
