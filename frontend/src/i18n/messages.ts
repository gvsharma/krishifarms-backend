import en from "../../messages/en.json";
import te from "../../messages/te.json";
import type { AppLocale } from "./config";
import type { MessageTree } from "./types";

const MESSAGES: Record<AppLocale, MessageTree> = {
  en: en as MessageTree,
  te: te as MessageTree,
};

export function getMessages(locale: AppLocale): MessageTree {
  return MESSAGES[locale] ?? MESSAGES.en;
}

function getNestedValue(tree: MessageTree, path: string): string | undefined {
  const parts = path.split(".");
  let current: unknown = tree;
  for (const part of parts) {
    if (!current || typeof current !== "object") return undefined;
    current = (current as Record<string, unknown>)[part];
  }
  return typeof current === "string" ? current : undefined;
}

export function translate(
  locale: AppLocale,
  key: string,
  vars?: Record<string, string | number>,
): string {
  const messages = getMessages(locale);
  const template = getNestedValue(messages, key) ?? getNestedValue(MESSAGES.en, key) ?? key;
  if (!vars) return template;
  return Object.entries(vars).reduce(
    (result, [name, value]) => result.replaceAll(`{${name}}`, String(value)),
    template,
  );
}

export function countLeafKeys(tree: MessageTree, prefix = ""): number {
  let count = 0;
  for (const [key, value] of Object.entries(tree)) {
    const path = prefix ? `${prefix}.${key}` : key;
    if (typeof value === "string") count += 1;
    else if (value && typeof value === "object") count += countLeafKeys(value as MessageTree, path);
  }
  return count;
}

export const TE_KEY_COUNT = countLeafKeys(te as MessageTree);
