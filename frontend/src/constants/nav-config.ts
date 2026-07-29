"use client";

import {
  AccountBalance,
  Agriculture,
  Analytics,
  Dashboard,
  Dataset,
  Handshake,
  HolidayVillage,
  Inventory2,
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
  label: string;
  /** i18n message key for translated label */
  labelKey?: string;
  icon: SvgIconComponent;
  /** Empty = visible to all authenticated roles. */
  roles?: NavRole[];
}

export interface NavSection {
  title: string;
  /** i18n message key for translated section title */
  titleKey?: string;
  items: NavItem[];
}

/** Role-aware nav matching backend module groups (W1 placeholders). */
export const NAV_SECTIONS: NavSection[] = [
  {
    title: "Overview",
    titleKey: "nav.overview",
    items: [
      { href: ROUTES.dashboard, label: "Dashboard", labelKey: "nav.dashboard", icon: Dashboard },
      {
        href: ROUTES.analytics,
        label: "Analytics",
        labelKey: "nav.analytics",
        icon: Analytics,
        roles: ["OWNER", "MANAGER", "ACCOUNTANT"],
      },
    ],
  },
  {
    title: "Operations",
    titleKey: "nav.operations",
    items: [
      {
        href: ROUTES.farmers,
        label: "Farmers",
        labelKey: "nav.farmers",
        icon: Agriculture,
        roles: ["OWNER", "MANAGER", "SUPERVISOR", "ACCOUNTANT"],
      },
      {
        href: ROUTES.villages,
        label: "Villages",
        labelKey: "nav.villages",
        icon: HolidayVillage,
        roles: ["OWNER", "MANAGER", "SUPERVISOR", "ACCOUNTANT", "AGENT", "DRIVER"],
      },
      {
        href: ROUTES.procurement,
        label: "Procurement",
        labelKey: "nav.procurement",
        icon: Spa,
        roles: ["OWNER", "MANAGER", "SUPERVISOR"],
      },
      {
        href: ROUTES.hamali,
        label: "Hamali",
        labelKey: "nav.hamali",
        icon: Inventory2,
        roles: ["OWNER", "MANAGER", "ACCOUNTANT"],
      },
      {
        href: ROUTES.services,
        label: "Field services",
        labelKey: "nav.fieldServices",
        icon: Handshake,
        roles: ["OWNER", "MANAGER", "SUPERVISOR", "AGENT", "DRIVER"],
      },
    ],
  },
  {
    title: "Finance",
    titleKey: "nav.finance",
    items: [
      {
        href: ROUTES.payments,
        label: "Finance",
        labelKey: "nav.payments",
        icon: AccountBalance,
        roles: ["OWNER", "MANAGER", "ACCOUNTANT"],
      },
    ],
  },
  {
    title: "System",
    titleKey: "nav.system",
    items: [
      {
        href: ROUTES.settingsUsers,
        label: "Users",
        labelKey: "nav.users",
        icon: People,
        roles: ["OWNER", "MANAGER"],
      },
      {
        href: ROUTES.settingsMasterData,
        label: "Master data",
        labelKey: "nav.masterData",
        icon: Dataset,
        roles: ["OWNER", "MANAGER"],
      },
      {
        href: ROUTES.settings,
        label: "Settings",
        labelKey: "nav.settings",
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
