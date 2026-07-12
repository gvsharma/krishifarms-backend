"use client";

import { useCallback } from "react";
import { translate } from "./messages";
import { useLocaleStore } from "@/stores/locale-store";

export function useTranslations() {
  const locale = useLocaleStore((s) => s.locale);

  const t = useCallback(
    (key: string, params?: Record<string, string | number>) => translate(locale, key, params),
    [locale],
  );

  return { t, locale };
}
