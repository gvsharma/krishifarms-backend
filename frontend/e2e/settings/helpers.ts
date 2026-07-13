/** @deprecated Import from `../utils` instead. Re-export for backward compatibility. */
export {
  ensureAuthenticated,
  expectListContent,
  expectNoPageErrors,
  expectShellTitle,
  FATAL_UI,
  trackPageErrors,
} from "../utils/common";

export {
  assertCreateDialogFieldsNotOverlapping,
  dialogField,
  expectDialogLabelsNotOverlapping,
  expectDialogTextContrast,
  expectLabeledFieldsNotOverlapping,
  openCatalogAddDialog,
} from "../utils/dialog";

export { heavyOverlap } from "../utils/overlap";

export {
  expectListOrEmptyOrError,
  expectSettingsShell,
  expectTableOrAlert,
  contentAlerts,
} from "../utils/shell";

export { enableDarkTheme, ensureDarkThemeViaToggle } from "../utils/theme";
