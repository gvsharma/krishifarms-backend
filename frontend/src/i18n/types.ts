import type en from "../../messages/en.json";
import type { AppLocale } from "./config";

export type Messages = typeof en;
export type Locale = AppLocale;

export interface MessageTree {
  [key: string]: string | MessageTree;
}
