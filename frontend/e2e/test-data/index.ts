import { e2eCredentials } from "../fixtures/auth";

/** Static test data for e2e scenarios. Extend per module as needed. */
export const testData = {
  credentials: e2eCredentials(),
  routes: {
    dashboard: "/dashboard",
    login: "/login",
    farmers: "/farmers",
    procurement: "/procurement",
    settings: "/settings",
    users: "/settings/users",
    villages: "/settings/villages",
  },
  labels: {
    dashboardTitle: /^Home$/i,
    farmOverview: /Farm operations overview/i,
  },
} as const;

export type TestData = typeof testData;
