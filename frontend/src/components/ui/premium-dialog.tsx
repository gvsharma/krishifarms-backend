"use client";

import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  type DialogActionsProps,
  type DialogContentProps,
  type DialogProps,
  type DialogTitleProps,
  type SxProps,
  type Theme,
} from "@mui/material";
import type { ReactNode } from "react";
import { premiumTokens } from "@/lib/design/premium";

const { colors } = premiumTokens;

/** @deprecated Prefer `premiumTokens.colors` — kept for SoftAlert / callers. */
export const adminChrome = {
  bg: colors.bg,
  primary: colors.primary,
  accent: colors.accent,
  border: colors.border,
} as const;

/**
 * Light premium chrome by default; dark mode follows MUI paper/text so
 * TextField / FormLabel / helper text stay visible (no white-on-#FAFAFA).
 */
const paperBaseSx: SxProps<Theme> = {
  borderRadius: "24px",
  bgcolor: colors.bg,
  border: `1px solid ${colors.border}`,
  boxShadow: "0 24px 48px -12px rgba(17, 24, 39, 0.18)",
  backgroundImage: "none",
  color: colors.primary,
  position: "relative",
  /** Ensure MUI form controls inherit scheme text (not stuck on light-only hex). */
  "& .MuiInputBase-input": { color: "text.primary" },
  "& .MuiInputBase-input::placeholder": { color: "text.secondary", opacity: 0.7 },
  "& .MuiFormLabel-root": { color: "text.secondary" },
  "& .MuiFormLabel-root.Mui-focused": { color: "primary.main" },
  "& .MuiFormHelperText-root": { color: "text.secondary" },
  "& .MuiSelect-icon": { color: "text.secondary" },
  "& .MuiFormControlLabel-label": { color: "text.primary" },
};

const paperDarkSx: SxProps<Theme> = (theme) =>
  theme.applyStyles("dark", {
    bgcolor: "background.paper",
    borderColor: "divider",
    color: "text.primary",
    boxShadow: "0 24px 48px -12px rgba(0, 0, 0, 0.55)",
  });

const backdropSx: SxProps<Theme> = [
  {
    backdropFilter: "blur(8px)",
    backgroundColor: "rgba(17, 24, 39, 0.28)",
  },
  (theme) =>
    theme.applyStyles("dark", {
      backgroundColor: "rgba(0, 0, 0, 0.55)",
    }),
];

export type PremiumDialogProps = Omit<DialogProps, "PaperProps" | "slotProps"> & {
  /** Optional extra Paper sx merged after premium defaults. */
  paperSx?: SxProps<Theme>;
};

function mergeSx(...parts: Array<SxProps<Theme> | undefined>): SxProps<Theme> {
  const out: Array<Exclude<SxProps<Theme>, ReadonlyArray<unknown>>> = [];
  for (const part of parts) {
    if (!part) continue;
    if (Array.isArray(part)) {
      for (const item of part) {
        if (item && item !== false) out.push(item as Exclude<SxProps<Theme>, ReadonlyArray<unknown>>);
      }
    } else {
      out.push(part as Exclude<SxProps<Theme>, ReadonlyArray<unknown>>);
    }
  }
  return out;
}

/**
 * Premium admin Dialog — blur backdrop, 24px radius, MUI focus trap.
 * Drop-in for settings/catalog create-edit and confirm dialogs.
 * Light palette aligned with `premiumTokens` / `.kf-premium`; dark mode uses MUI paper.
 */
export function PremiumDialog({
  children,
  paperSx: paperSxProp,
  ...props
}: PremiumDialogProps) {
  return (
    <Dialog
      fullWidth
      {...props}
      slotProps={{
        backdrop: { sx: backdropSx },
        root: { sx: { zIndex: (theme) => theme.zIndex.modal } },
        paper: {
          sx: mergeSx(
            paperBaseSx,
            { zIndex: (theme) => theme.zIndex.modal + 1 },
            paperDarkSx,
            paperSxProp,
          ),
        },
      }}
    >
      {children}
    </Dialog>
  );
}

export function PremiumDialogTitle({ children, sx, ...props }: DialogTitleProps) {
  return (
    <DialogTitle
      {...props}
      sx={mergeSx(
        {
          color: colors.primary,
          fontWeight: 600,
          fontSize: "1.125rem",
          letterSpacing: "-0.01em",
          px: 3,
          pt: 2.5,
          pb: 1,
        },
        (theme) => theme.applyStyles("dark", { color: "text.primary" }),
        sx,
      )}
    >
      {children}
    </DialogTitle>
  );
}

export function PremiumDialogContent({ children, sx, ...props }: DialogContentProps) {
  return (
    <DialogContent
      {...props}
      sx={mergeSx(
        {
          px: 3,
          pt: 1,
          pb: 1,
          color: colors.primary,
          // Keep labels / first control from clipping under the title
          overflow: "visible",
        },
        (theme) => theme.applyStyles("dark", { color: "text.primary" }),
        sx,
      )}
    >
      {children}
    </DialogContent>
  );
}

export function PremiumDialogActions({ children, sx, ...props }: DialogActionsProps) {
  return (
    <DialogActions
      {...props}
      sx={mergeSx(
        {
          px: 3,
          py: 2,
          gap: 1,
          borderTop: `1px solid ${colors.border}`,
        },
        (theme) => theme.applyStyles("dark", { borderColor: "divider" }),
        sx,
      )}
    >
      {children}
    </DialogActions>
  );
}

export type PremiumDialogChromeProps = {
  open: boolean;
  onClose: () => void;
  title: ReactNode;
  children: ReactNode;
  actions: ReactNode;
  maxWidth?: DialogProps["maxWidth"];
};

/** Convenience shell: title + content + actions with shared chrome. */
export function PremiumDialogChrome({
  open,
  onClose,
  title,
  children,
  actions,
  maxWidth = "sm",
}: PremiumDialogChromeProps) {
  return (
    <PremiumDialog open={open} onClose={onClose} maxWidth={maxWidth}>
      <PremiumDialogTitle>{title}</PremiumDialogTitle>
      <PremiumDialogContent>{children}</PremiumDialogContent>
      <PremiumDialogActions>{actions}</PremiumDialogActions>
    </PremiumDialog>
  );
}
