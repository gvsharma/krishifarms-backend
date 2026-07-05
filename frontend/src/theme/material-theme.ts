"use client";

import { createTheme } from "@mui/material/styles";

/** Agri green MD3 palette — aligned with frontend/src/lib/design/tokens.ts */
const agriPrimary = {
  main: "#2D6A4F",
  light: "#40916C",
  dark: "#1B4332",
  contrastText: "#FFFFFF",
};

const agriSecondary = {
  main: "#40916C",
  light: "#52B788",
  dark: "#2D6A4F",
  contrastText: "#FFFFFF",
};

const helveticaStack = '"Helvetica Neue", Helvetica, Arial, sans-serif';

export const materialTheme = createTheme({
  cssVariables: {
    colorSchemeSelector: "class",
  },
  colorSchemes: {
    light: {
      palette: {
        primary: agriPrimary,
        secondary: agriSecondary,
        success: { main: "#1B7F5A" },
        warning: { main: "#B45309" },
        error: { main: "#BA1A1A" },
        background: {
          default: "#FAFAF9",
          paper: "#FFFFFF",
        },
      },
    },
    dark: {
      palette: {
        primary: {
          main: "#52B788",
          light: "#74C69D",
          dark: "#40916C",
          contrastText: "#0D1F17",
        },
        secondary: {
          main: "#74C69D",
          light: "#95D5B2",
          dark: "#52B788",
          contrastText: "#0D1F17",
        },
        success: { main: "#52B788" },
        warning: { main: "#D97706" },
        error: { main: "#F87171" },
        background: {
          default: "#0F1410",
          paper: "#1A211C",
        },
      },
    },
  },
  typography: {
    fontFamily: helveticaStack,
    h1: { fontWeight: 600, letterSpacing: "-0.02em" },
    h2: { fontWeight: 600, letterSpacing: "-0.02em" },
    h3: { fontWeight: 600, letterSpacing: "-0.01em" },
    h4: { fontWeight: 600 },
    h5: { fontWeight: 600 },
    h6: { fontWeight: 600 },
    subtitle1: { fontWeight: 500 },
    subtitle2: { fontWeight: 500 },
    button: { textTransform: "none", fontWeight: 500 },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          fontFamily: helveticaStack,
        },
      },
    },
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
      styleOverrides: {
        root: { borderRadius: 10 },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: "1px solid",
          borderColor: "var(--mui-palette-divider)",
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          marginInline: 8,
          marginBlock: 2,
        },
      },
    },
    MuiAppBar: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          borderBottom: "1px solid",
          borderColor: "var(--mui-palette-divider)",
          backdropFilter: "blur(12px)",
        },
      },
    },
    MuiCard: {
      defaultProps: { elevation: 0 },
      styleOverrides: {
        root: {
          border: "1px solid",
          borderColor: "var(--mui-palette-divider)",
        },
      },
    },
  },
});

export const DRAWER_WIDTH = 260;
export const DRAWER_WIDTH_COLLAPSED = 72;
