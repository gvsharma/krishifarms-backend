"use client";

import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter";
import CssBaseline from "@mui/material/CssBaseline";
import GlobalStyles from "@mui/material/GlobalStyles";
import { ThemeProvider, useColorScheme } from "@mui/material/styles";
import { useTheme } from "next-themes";
import { useEffect, useMemo, type ReactNode } from "react";
import { materialTheme } from "./material-theme";

function MuiColorSchemeSync({ children }: { children: ReactNode }) {
  const { resolvedTheme } = useTheme();
  const { setMode } = useColorScheme();

  useEffect(() => {
    const root = document.documentElement;
    if (resolvedTheme === "dark") {
      root.classList.add("dark");
      setMode("dark");
    } else if (resolvedTheme === "light") {
      root.classList.remove("dark");
      setMode("light");
    }
  }, [resolvedTheme, setMode]);

  return <>{children}</>;
}

export function ThemeRegistry({ children }: { children: ReactNode }) {
  const theme = useMemo(() => materialTheme, []);

  return (
    <AppRouterCacheProvider options={{ enableCssLayer: true }}>
      <ThemeProvider theme={theme} defaultMode="light" disableTransitionOnChange>
        <GlobalStyles styles="@layer theme, base, mui, components, utilities;" />
        <CssBaseline enableColorScheme />
        <MuiColorSchemeSync>{children}</MuiColorSchemeSync>
      </ThemeProvider>
    </AppRouterCacheProvider>
  );
}
