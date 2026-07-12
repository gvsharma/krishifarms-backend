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
  expectLabeledFieldsNotOverlapping,
  openCatalogAddDialog,
} from "../utils/dialog";

export { heavyOverlap } from "../utils/overlap";

export {
  expectListOrEmptyOrError,
  expectSettingsShell,
  expectTableOrAlert,
} from "../utils/shell";
