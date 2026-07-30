"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { useState, type ReactNode } from "react";
import { AuthBootstrap } from "@/features/auth/bootstrap";
import { LocaleProvider } from "@/components/i18n/locale-provider";
import { makeQueryClient } from "@/lib/query/query-client";
import { ThemeRegistry } from "@/theme/theme-registry";

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => makeQueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
        <ThemeRegistry>
          <AuthBootstrap>
            <LocaleProvider>{children}</LocaleProvider>
          </AuthBootstrap>
        </ThemeRegistry>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
