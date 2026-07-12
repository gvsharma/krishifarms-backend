/** Shared test routes and labels for smoke/regression suites. */
export const ROUTES = {
  dashboard: "/dashboard",
  login: "/login",
  farmers: "/farmers",
  farmerNew: "/farmers/new",
  settings: "/settings",
  settingsUsers: "/settings/users",
  settingsVillages: "/settings/villages",
  settingsMasterData: "/settings/master-data",
  masterDataCrops: "/settings/master-data/crops",
  masterDataBuyers: "/settings/master-data/buyers",
} as const;

export const PAGE_NAMES: Record<string, string> = {
  [ROUTES.dashboard]: "dashboard",
  [ROUTES.farmers]: "farmers-list",
  [ROUTES.farmerNew]: "farmers-create",
  [ROUTES.settingsUsers]: "settings-users",
  [ROUTES.settingsVillages]: "settings-villages",
  [ROUTES.settingsMasterData]: "settings-master-data",
  [ROUTES.masterDataCrops]: "master-data-crops",
  [ROUTES.masterDataBuyers]: "master-data-buyers",
};
