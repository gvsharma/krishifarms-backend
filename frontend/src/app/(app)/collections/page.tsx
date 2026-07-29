"use client";

import { Wallet } from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";

export default function CollectionsPage() {
  return (
    <PlaceholderPage
      titleKey="pages.collections"
      descriptionKey="pages.collectionsDesc"
      icon={Wallet}
    />
  );
}
