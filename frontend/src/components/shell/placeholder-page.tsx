"use client";

import type { LucideIcon } from "lucide-react";
import { PageShell } from "@/components/shell/page-shell";
import { EmptyState } from "@/components/shell/empty-state";
import { useTranslation } from "@/i18n/use-translation";

interface PlaceholderPageProps {
  titleKey: string;
  descriptionKey: string;
  icon: LucideIcon;
}

export function PlaceholderPage({ titleKey, descriptionKey, icon }: PlaceholderPageProps) {
  const { t } = useTranslation();
  const title = t(titleKey as Parameters<typeof t>[0]);

  return (
    <PageShell title={title} description={t(descriptionKey as Parameters<typeof t>[0])}>
      <EmptyState
        icon={icon}
        title={t("common.comingSoonTitle", { title })}
        description={t("common.comingSoonDescription")}
      />
    </PageShell>
  );
}
