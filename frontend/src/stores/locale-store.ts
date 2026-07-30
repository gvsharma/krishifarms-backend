import { create } from "zustand";
import { persist } from "zustand/middleware";
import { normalizeLocale, type AppLocale } from "@/i18n/messages";

interface LocaleState {
  locale: AppLocale;
  setLocale: (locale: AppLocale) => void;
  hydrateFromUser: (preferredLocale: string | null | undefined) => void;
}

export const useLocaleStore = create<LocaleState>()(
  persist(
    (set, get) => ({
      locale: "en",
      setLocale: (locale) => set({ locale }),
      hydrateFromUser: (preferredLocale) => {
        const normalized = normalizeLocale(preferredLocale);
        if (normalized !== get().locale) {
          set({ locale: normalized });
        }
      },
    }),
    { name: "krishi-locale" },
  ),
);

/** Read persisted locale outside React (API client). */
export function getPersistedLocale(): AppLocale {
  if (typeof window === "undefined") return "en";
  try {
    const raw = localStorage.getItem("krishi-locale");
    if (!raw) return "en";
    const parsed = JSON.parse(raw) as { state?: { locale?: string } };
    return normalizeLocale(parsed.state?.locale);
  } catch {
    return "en";
  }
}
