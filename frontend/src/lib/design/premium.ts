/**
 * Premium form-control design tokens (Linear / Stripe / Apple-inspired).
 * Scoped to `.kf-premium` — does not replace the MUI shell palette.
 * Mirrors `frontend/src/styles/premium.css`.
 */
export const premiumTokens = {
  colors: {
    bg: "#FAFAFA",
    surface: "#FFFFFF",
    primary: "#111827",
    primaryForeground: "#FFFFFF",
    accent: "#E11D48",
    accentForeground: "#FFFFFF",
    secondaryAccent: "#C084FC",
    border: "#E5E7EB",
    borderStrong: "#D1D5DB",
    muted: "#F3F4F6",
    mutedForeground: "#6B7280",
    placeholder: "#9CA3AF",
    success: "#16A34A",
    error: "#DC2626",
    focusRing: "rgba(17, 24, 39, 0.12)",
    focusRingAccent: "rgba(225, 29, 72, 0.18)",
  },
  control: {
    height: "52px",
    radius: "16px",
    paddingX: "16px",
    paddingY: "14px",
    fontSize: "15px",
    lineHeight: "22px",
  },
  button: {
    height: "48px",
    heightSm: "40px",
    radius: "14px",
    fontSize: "15px",
    fontWeight: 600,
  },
  motion: {
    fast: "120ms",
    normal: "180ms",
    easing: "cubic-bezier(0.22, 1, 0.36, 1)",
  },
  fonts: {
    heading: "var(--font-plus-jakarta), ui-sans-serif, system-ui, sans-serif",
    body: "var(--font-inter), ui-sans-serif, system-ui, sans-serif",
  },
} as const;

export type PremiumTokens = typeof premiumTokens;
