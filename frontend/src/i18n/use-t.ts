"use client";

import { useCallback } from "react";
import { translate } from "./messages";
import { useLocaleStore } from "@/stores/locale-store";

/** Dot-path translator (e.g. `common.save`) backed by JSON message catalogs. */
export function useT() {
  const locale = useLocaleStore((s) => s.locale);

  return useCallback(
    (key: string, params?: Record<string, string | number>) => translate(locale, key, params),
    [locale],
  );
}
