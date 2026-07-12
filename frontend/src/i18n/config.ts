export const LOCALES = ["en", "te"] as const;

export type AppLocale = (typeof LOCALES)[number];

export const DEFAULT_LOCALE: AppLocale = "en";

export function isAppLocale(value: string | null | undefined): value is AppLocale {
  return value === "en" || value === "te";
}
