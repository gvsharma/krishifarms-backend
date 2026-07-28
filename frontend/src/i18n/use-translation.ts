"use client";

import { useCallback } from "react";
import { translate, type AppLocale, type MessageKey } from "./messages";
import { useLocaleStore } from "@/stores/locale-store";

export function useTranslation() {
  const locale = useLocaleStore((s) => s.locale);

  const t = useCallback(
    (key: MessageKey, params?: Record<string, string>) => translate(locale, key, params),
    [locale],
  );

  return { t, locale };
}

export function useLocale(): AppLocale {
  return useLocaleStore((s) => s.locale);
}
