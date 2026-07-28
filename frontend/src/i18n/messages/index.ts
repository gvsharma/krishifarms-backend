import { enMessages } from "./en";
import { teMessages } from "./te";

export type AppLocale = "en" | "te";

export const messages = {
  en: enMessages,
  te: teMessages,
} as const;

export type MessageKey = keyof typeof enMessages;

export function normalizeLocale(value: string | null | undefined): AppLocale {
  if (!value) return "en";
  const lower = value.toLowerCase();
  if (lower.startsWith("te")) return "te";
  return "en";
}

export function translate(
  locale: AppLocale,
  key: MessageKey,
  params?: Record<string, string>,
): string {
  const template = messages[locale][key] ?? messages.en[key] ?? key;
  if (!params) return template;
  return Object.entries(params).reduce(
    (text, [param, value]) => text.replaceAll(`{${param}}`, value),
    template,
  );
}
