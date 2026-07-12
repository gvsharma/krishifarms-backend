"use client";

import { Alert, type AlertProps } from "@mui/material";
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

/**
 * Soft inline Alert for form save failures / soft API errors on admin screens.
 * Matches premium chrome (accent rose for errors, muted borders).
 */
export function SoftAlert({ severity = "error", sx, variant, ...props }: SoftAlertProps) {
  const tone = softBySeverity[severity];
  return (
    <Alert
      severity={severity}
      variant={variant ?? "outlined"}
      {...props}
      sx={{
        borderRadius: "12px",
        bgcolor: tone.bgcolor,
        color: tone.color,
        borderColor: tone.borderColor,
        alignItems: "center",
        "& .MuiAlert-icon": { color: tone.color },
        "& .MuiAlert-message": { color: tone.color, fontSize: "0.875rem" },
        ...sx,
      }}
    />
  );
}
