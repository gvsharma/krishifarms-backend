"use client";

import type { LucideIcon } from "lucide-react";
import { PageShell } from "@/components/shell/page-shell";
import { EmptyState } from "@/components/shell/empty-state";
import { useTranslations } from "@/i18n/use-translations";

interface PlaceholderPageProps {
  title: string;
  description: string;
  icon: LucideIcon;
}

export function PlaceholderPage({ title, description, icon }: PlaceholderPageProps) {
  const { t } = useTranslations();

  return (
    <PageShell title={title} description={description}>
      <EmptyState
        icon={icon}
        title={t("common.comingSoonTitle", { title })}
        description={t("common.comingSoonDescription")}
      />
    </PageShell>
  );
}
