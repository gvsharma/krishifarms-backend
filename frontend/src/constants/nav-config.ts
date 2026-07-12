"use client";

import {
  AccountBalance,
  Agriculture,
  Dashboard,
  Dataset,
  Handshake,
  People,
  Settings,
  Spa,
} from "@mui/icons-material";
import type { SvgIconComponent } from "@mui/icons-material";
import { ROUTES } from "@/constants/routes";

/** Role codes aligned with backend RBAC. */
export type NavRole = "OWNER" | "MANAGER" | "SUPERVISOR" | "AGENT" | "DRIVER" | "WORKER" | "ACCOUNTANT";

export interface NavItem {
  href: string;
  /** next-intl message key under `nav.items`. */
  labelKey:
    | "dashboard"
    | "farmers"
    | "procurement"
    | "services"
    | "finance"
    | "users"
    | "masterData"
    | "settings";
  icon: SvgIconComponent;
  /** Empty = visible to all authenticated roles. */
  roles?: NavRole[];
}

export interface NavSection {
  /** next-intl message key under `nav.sections`. */
  titleKey: "overview" | "operations" | "finance" | "system";
  items: NavItem[];
}

/** Role-aware nav matching backend module groups (W1 placeholders). */
export const NAV_SECTIONS: NavSection[] = [
  {
    titleKey: "overview",
    items: [{ href: ROUTES.dashboard, labelKey: "dashboard", icon: Dashboard }],
  },
  {
    titleKey: "operations",
    items: [
      { href: ROUTES.farmers, labelKey: "farmers", icon: Agriculture },
      { href: ROUTES.procurement, labelKey: "procurement", icon: Spa },
      {
        href: ROUTES.services,
        labelKey: "services",
        icon: Handshake,
        roles: ["OWNER", "MANAGER", "AGENT"],
      },
    ],
  },
  {
    titleKey: "finance",
    items: [
      {
        href: ROUTES.payments,
        labelKey: "finance",
        icon: AccountBalance,
        roles: ["OWNER", "MANAGER", "ACCOUNTANT"],
      },
    ],
  },
  {
    titleKey: "system",
    items: [
      {
        href: ROUTES.settingsUsers,
        labelKey: "users",
        icon: People,
        roles: ["OWNER", "MANAGER"],
      },
      {
        href: ROUTES.settingsMasterData,
        labelKey: "masterData",
        icon: Dataset,
        roles: ["OWNER", "MANAGER"],
      },
      {
        href: ROUTES.settings,
        labelKey: "settings",
        icon: Settings,
        roles: ["OWNER", "MANAGER"],
      },
    ],
  },
];

export function filterNavByRole(sections: NavSection[], role: NavRole): NavSection[] {
  return sections
    .map((section) => ({
      ...section,
      items: section.items.filter((item) => !item.roles || item.roles.includes(role)),
    }))
    .filter((section) => section.items.length > 0);
}
