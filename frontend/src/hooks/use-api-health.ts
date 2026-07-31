"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchApiHealth } from "@/lib/api/health";

export function useApiHealth() {
  return useQuery({
    queryKey: ["api-health"],
    queryFn: async () => {
      const ok = await fetchApiHealth();
      if (!ok) throw new Error("API unreachable");
      return true;
    },
    retry: 1,
    retryDelay: 2_000,
    staleTime: 30_000,
    refetchInterval: (query) => (query.state.status === "error" ? 30_000 : 120_000),
    refetchOnWindowFocus: true,
  });
}
