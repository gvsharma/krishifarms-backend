"use client";

import {
  Package,
  Receipt,
  Sprout,
  Truck,
  Users,
  Wallet,
  type LucideIcon,
} from "lucide-react";
import { PlaceholderPage } from "@/components/shell/placeholder-page";
import { useTranslations } from "@/i18n/use-translations";

const PLACEHOLDER_ICONS = {
  farms: Sprout,
  vehicles: Truck,
  workers: Users,
  expenses: Receipt,
  payments: Wallet,
  collections: Package,
} as const satisfies Record<string, LucideIcon>;

export type OperationsPlaceholderKey = keyof typeof PLACEHOLDER_ICONS;

interface OperationsPlaceholderProps {
  placeholderKey: OperationsPlaceholderKey;
}

export function OperationsPlaceholder({ placeholderKey }: OperationsPlaceholderProps) {
  const { t } = useTranslations();
  const Icon = PLACEHOLDER_ICONS[placeholderKey];

  return (
    <PlaceholderPage
      title={t(`operations.placeholders.${placeholderKey}.title`)}
      description={t(`operations.placeholders.${placeholderKey}.description`)}
      icon={Icon}
    />
  );
}
