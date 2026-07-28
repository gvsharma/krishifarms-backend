"use client";

import { Tractor } from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";

export default function WorkersPage() {
  return (
    <PlaceholderPage
      titleKey="pages.workers"
      descriptionKey="pages.workersDesc"
      icon={Tractor}
    />
  );
}
