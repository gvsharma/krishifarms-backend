"use client";

import { useEffect } from "react";
import { useLocaleStore } from "@/stores/locale-store";
import { useAuth } from "@/hooks/use-auth";

/** Syncs html lang, Telugu font class, and user preferred_locale from the API. */
export function LocaleProvider({ children }: { children: React.ReactNode }) {
  const locale = useLocaleStore((s) => s.locale);
  const hydrateFromUser = useLocaleStore((s) => s.hydrateFromUser);
  const { user } = useAuth();

  useEffect(() => {
    if (user?.preferred_locale) {
      hydrateFromUser(user.preferred_locale);
    }
  }, [user?.preferred_locale, hydrateFromUser]);

  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.classList.toggle("locale-te", locale === "te");
  }, [locale]);

  return <>{children}</>;
}
