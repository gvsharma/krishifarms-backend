/**
 * KrishiFarms design tokens — mirrors globals.css for programmatic use.
 * Inspired by Farm Management SaaS dashboard (Dribbble #27437443).
 */
export const tokens = {
  colors: {
    primary: "#2D6A4F",
    primaryLight: "#40916C",
    primaryContainer: "#D8F3DC",
    secondary: "#40916C",
    harvest: "#BC6C25",
    surface: "#FAFAF9",
    card: "#FFFFFF",
    sidebar: "#FFFFFF",
    success: "#1B7F5A",
    warning: "#B45309",
    error: "#BA1A1A",
  },
  layout: {
    sidebarExpanded: "260px",
    sidebarCollapsed: "72px",
    headerHeight: "64px",
    maxContentWidth: "1440px",
  },
  radius: {
    sm: "0.375rem",
    md: "0.5rem",
    lg: "0.75rem",
    xl: "1rem",
    "2xl": "1.25rem",
  },
  motion: {
    fast: "150ms",
    normal: "250ms",
    slow: "350ms",
    easing: "cubic-bezier(0.22, 1, 0.36, 1)",
  },
} as const;

export const DRIBBBLE_INSPIRATION_URL =
  "https://dribbble.com/shots/27437443-Farm-Management-SaaS-Dashboard";
