"use client";

import { BarChart3 } from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";
import { useTranslations } from "@/i18n/use-translations";

export function ReportsPlaceholder() {
  const { t } = useTranslations();

  return (
    <PlaceholderPage
      title={t("reports.title")}
      description={t("reports.description")}
      icon={BarChart3}
    />
  );
}
