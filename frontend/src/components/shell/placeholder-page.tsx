import type { LucideIcon } from "lucide-react";
import { PageShell } from "@/components/shell/page-shell";
import { EmptyState } from "@/components/shell/empty-state";

interface PlaceholderPageProps {
  title: string;
  description: string;
  icon: LucideIcon;
}

export function PlaceholderPage({ title, description, icon }: PlaceholderPageProps) {
  return (
    <PageShell title={title} description={description}>
      <EmptyState
        icon={icon}
        title={`${title} — coming soon`}
        description="This module will connect to Phase 2+ API endpoints. The app shell, navigation, and design system are ready."
      />
    </PageShell>
  );
}
