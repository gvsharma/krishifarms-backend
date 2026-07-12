"use client";

import { useEffect } from "react";
import { useAuth } from "@/hooks/use-auth";
import { isAppLocale } from "@/i18n/config";
import { setAppLocale, useLocaleStore } from "@/stores/locale-store";

/** Hydrates locale from profile + syncs `html[lang]` and Telugu font class. */
export function LocaleSync() {
  const locale = useLocaleStore((s) => s.locale);
  const { user } = useAuth();

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!localStorage.getItem("krishi-locale") && isAppLocale(user?.preferred_locale)) {
      setAppLocale(user?.preferred_locale);
    }
  }, [user?.preferred_locale]);

  useEffect(() => {
    document.documentElement.lang = locale;
    document.body.classList.toggle("locale-te", locale === "te");
  }, [locale]);

  return null;
}
