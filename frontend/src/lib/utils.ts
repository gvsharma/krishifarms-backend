import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { AppLocale } from "@/stores/locale-store";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

function intlLocale(locale?: AppLocale): string {
  return locale === "te" ? "te-IN" : "en-IN";
}

export function formatCurrency(amount: number, locale?: AppLocale): string {
  return new Intl.NumberFormat(intlLocale(locale), {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatCompact(value: number, unit?: string, locale?: AppLocale): string {
  const formatted = new Intl.NumberFormat(intlLocale(locale), {
    notation: value >= 100000 ? "compact" : "standard",
    maximumFractionDigits: 1,
  }).format(value);
  return unit ? `${formatted} ${unit}` : formatted;
}

export function formatPercent(value: number, signed = true): string {
  const prefix = signed && value > 0 ? "+" : "";
  return `${prefix}${value.toFixed(1)}%`;
}

export function formatDateDisplay(iso: string, locale?: AppLocale): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return new Intl.DateTimeFormat(intlLocale(locale), {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
}
