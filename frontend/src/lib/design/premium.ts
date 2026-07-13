/**
 * Premium form-control design tokens (Linear / Stripe / Apple-inspired).
 * Scoped to `.kf-premium` — does not replace the MUI shell palette.
 * Mirrors `frontend/src/styles/premium.css` (including `.dark .kf-premium`).
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
  /** Dark overrides applied via CSS under `.dark .kf-premium`. */
  colorsDark: {
    bg: "#1A211C",
    surface: "#242B26",
    primary: "#F3F4F6",
    primaryForeground: "#0F1410",
    border: "#2F3A34",
    borderStrong: "#3D4A43",
    muted: "#1F2823",
    mutedForeground: "#9CA3AF",
    placeholder: "#6B7280",
    focusRing: "rgba(243, 244, 246, 0.14)",
    focusRingAccent: "rgba(251, 113, 133, 0.28)",
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
