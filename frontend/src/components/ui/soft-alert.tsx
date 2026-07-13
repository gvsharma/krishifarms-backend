"use client";

import { Alert, type AlertProps, type SxProps, type Theme } from "@mui/material";
import { premiumTokens } from "@/lib/design/premium";

export type SoftAlertProps = AlertProps;

const { colors } = premiumTokens;

const softBySeverity: Record<
  NonNullable<AlertProps["severity"]>,
  { bgcolor: string; color: string; borderColor: string }
> = {
  error: {
    bgcolor: "#FFF1F2",
    color: colors.accent,
    borderColor: "#FECDD3",
  },
  warning: {
    bgcolor: "#FFFBEB",
    color: "#B45309",
    borderColor: "#FDE68A",
  },
  info: {
    bgcolor: colors.muted,
    color: colors.primary,
    borderColor: colors.border,
  },
  success: {
    bgcolor: "#ECFDF5",
    color: colors.success,
    borderColor: "#A7F3D0",
  },
};

/** Dark-mode tones — readable on premium / MUI dark paper. */
const softBySeverityDark: Record<
  NonNullable<AlertProps["severity"]>,
  { bgcolor: string; color: string; borderColor: string }
> = {
  error: {
    bgcolor: "rgba(225, 29, 72, 0.16)",
    color: "#FDA4AF",
    borderColor: "rgba(251, 113, 133, 0.45)",
  },
  warning: {
    bgcolor: "rgba(180, 83, 9, 0.18)",
    color: "#FCD34D",
    borderColor: "rgba(251, 191, 36, 0.4)",
  },
  info: {
    bgcolor: "rgba(148, 163, 184, 0.12)",
    color: "#E5E7EB",
    borderColor: "rgba(148, 163, 184, 0.35)",
  },
  success: {
    bgcolor: "rgba(22, 163, 74, 0.16)",
    color: "#86EFAC",
    borderColor: "rgba(74, 222, 128, 0.4)",
  },
};

/**
 * Soft inline Alert for form save failures / soft API errors on admin screens.
 * Matches premium chrome (accent rose for errors, muted borders); dark variants included.
 */
export function SoftAlert({ severity = "error", sx, variant, ...props }: SoftAlertProps) {
  const tone = softBySeverity[severity];
  const toneDark = softBySeverityDark[severity];
  const softSx: SxProps<Theme> = [
    {
      borderRadius: "12px",
      bgcolor: tone.bgcolor,
      color: tone.color,
      borderColor: tone.borderColor,
      alignItems: "center",
      "& .MuiAlert-icon": { color: tone.color },
      "& .MuiAlert-message": { color: tone.color, fontSize: "0.875rem" },
    },
    (theme) =>
      theme.applyStyles("dark", {
        bgcolor: toneDark.bgcolor,
        color: toneDark.color,
        borderColor: toneDark.borderColor,
        "& .MuiAlert-icon": { color: toneDark.color },
        "& .MuiAlert-message": { color: toneDark.color },
      }),
    ...(Array.isArray(sx) ? sx : sx ? [sx] : []),
  ];
  return (
    <Alert severity={severity} variant={variant ?? "outlined"} {...props} sx={softSx} />
  );
}
