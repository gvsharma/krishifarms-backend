"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { useState, type ReactNode } from "react";
import { makeQueryClient } from "@/lib/query/query-client";
import { ThemeRegistry } from "@/theme/theme-registry";

export function Providers({ children }: { children: ReactNode }) {
  const [queryClient] = useState(() => makeQueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
        <ThemeRegistry>{children}</ThemeRegistry>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
