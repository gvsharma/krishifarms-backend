import { create } from "zustand";
import { persist } from "zustand/middleware";
import { DEFAULT_LOCALE, isAppLocale, type AppLocale } from "@/i18n/config";

export type { AppLocale };

interface LocaleState {
  locale: AppLocale;
  setLocale: (locale: AppLocale) => void;
}

export const useLocaleStore = create<LocaleState>()(
  persist(
    (set) => ({
      locale: DEFAULT_LOCALE,
      setLocale: (locale) => set({ locale }),
    }),
    { name: "krishi-locale" },
  ),
);

/** Non-hook read for API client interceptors. */
export function getAppLocale(): AppLocale {
  return useLocaleStore.getState().locale;
}

export function setAppLocale(locale: string | null | undefined): void {
  if (isAppLocale(locale)) {
    useLocaleStore.getState().setLocale(locale);
  }
}
