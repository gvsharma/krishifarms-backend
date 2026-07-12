export const SITE_NAME = "KrishiFarms";

export const ROUTES = {
  dashboard: "/dashboard",
  farmers: "/farmers",
  farms: "/farms",
  collections: "/collections",
  procurement: "/procurement",
  services: "/field-services",
  payments: "/payments",
  expenses: "/expenses",
  vehicles: "/vehicles",
  workers: "/workers",
  reports: "/reports",
  settings: "/settings",
  settingsUsers: "/settings/users",
  settingsVillages: "/settings/villages",
  settingsMasterData: "/settings/master-data",
} as const;

export type AppRoute = (typeof ROUTES)[keyof typeof ROUTES];
