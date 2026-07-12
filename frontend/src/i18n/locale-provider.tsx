"use client";

import type { ReactNode } from "react";

/** Locale is driven by Zustand + `@/i18n/use-translations`; this wrapper keeps the provider tree stable. */
export function LocaleProvider({ children }: { children: ReactNode }) {
  return children;
}
