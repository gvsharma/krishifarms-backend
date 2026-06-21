export const ROUTES = {
  dashboard: "/dashboard",
  farmers: "/farmers",
  farms: "/farms",
  collections: "/collections",
  procurement: "/procurement",
  payments: "/payments",
  expenses: "/expenses",
  vehicles: "/vehicles",
  workers: "/workers",
  reports: "/reports",
  settings: "/settings",
} as const;

export type AppRoute = (typeof ROUTES)[keyof typeof ROUTES];

export const SITE_NAME = "KrishiFarms";
