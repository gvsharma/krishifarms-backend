import type { AppLocale } from "@/i18n/messages";

/** Pick display string for API rows with optional Telugu. */
export function pickBilingual(
  locale: AppLocale,
  en: string | null | undefined,
  te: string | null | undefined,
): string {
  if (locale === "te" && te?.trim()) return te.trim();
  return en?.trim() ?? "";
}

/** Dropdown label: primary locale + secondary in parentheses when both exist. */
export function formatMasterOptionLabel(
  locale: AppLocale,
  en: string | null | undefined,
  te: string | null | undefined,
): string {
  const primary = pickBilingual(locale, en, te);
  if (!primary) return en?.trim() ?? te?.trim() ?? "";
  const secondary = locale === "te" ? en?.trim() : te?.trim();
  if (secondary && secondary !== primary) {
    return `${primary} · ${secondary}`;
  }
  return primary;
}

/** Static Telugu for district/mandal masters (no name_te column yet). */
const DISTRICT_TE: Record<string, string> = {
  Rangareddy: "రంగారెడ్డి",
  Nizamabad: "నిజామాబాద్",
};

const MANDAL_TE: Record<string, string> = {
  Keshampeta: "కేశంపేట",
  Kothur: "కొత్తూర్",
  Talakondapally: "తలకొండపల్లి",
  Maheshwaram: "మహేశ్వరం",
  Farooqnagar: "ఫరూఖ్‌నగర్",
};

export function districtLabel(locale: AppLocale, name: string): string {
  return formatMasterOptionLabel(locale, name, DISTRICT_TE[name]);
}

export function mandalLabel(locale: AppLocale, name: string): string {
  return formatMasterOptionLabel(locale, name, MANDAL_TE[name]);
}
