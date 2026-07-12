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

const paperSx = {
  borderRadius: "24px",
  bgcolor: colors.bg,
  border: `1px solid ${colors.border}`,
  boxShadow: "0 24px 48px -12px rgba(17, 24, 39, 0.18)",
  backgroundImage: "none",
} as const;

const backdropSx = {
  backdropFilter: "blur(8px)",
  backgroundColor: "rgba(17, 24, 39, 0.28)",
} as const;

export type PremiumDialogProps = Omit<DialogProps, "PaperProps" | "slotProps"> & {
  /** Optional extra Paper sx merged after premium defaults. */
  paperSx?: DialogProps["sx"];
};

/**
 * Premium admin Dialog — blur backdrop, 24px radius, MUI focus trap.
 * Drop-in for settings/catalog create-edit and confirm dialogs.
 * Palette aligned with `premiumTokens` / `.kf-premium`.
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
        paper: {
          sx: {
            ...paperSx,
            ...(typeof paperSxProp === "object" && paperSxProp !== null ? paperSxProp : {}),
          },
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
      sx={{
        color: colors.primary,
        fontWeight: 600,
        fontSize: "1.125rem",
        letterSpacing: "-0.01em",
        px: 3,
        pt: 2.5,
        pb: 1,
        ...sx,
      }}
    >
      {children}
    </DialogTitle>
  );
}

export function PremiumDialogContent({ children, sx, ...props }: DialogContentProps) {
  return (
    <DialogContent
      {...props}
      sx={{
        px: 3,
        pt: 1,
        pb: 1,
        color: colors.primary,
        // Keep labels / first control from clipping under the title
        overflow: "visible",
        ...sx,
      }}
    >
      {children}
    </DialogContent>
  );
}

export function PremiumDialogActions({ children, sx, ...props }: DialogActionsProps) {
  return (
    <DialogActions
      {...props}
      sx={{
        px: 3,
        py: 2,
        gap: 1,
        borderTop: `1px solid ${colors.border}`,
        ...sx,
      }}
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
