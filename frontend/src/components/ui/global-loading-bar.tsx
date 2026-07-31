"use client";

import { LinearProgress } from "@mui/material";
import { useIsFetching, useIsMutating } from "@tanstack/react-query";

/** Top-of-screen progress while any TanStack Query fetch/mutation is in flight. */
export function GlobalLoadingBar() {
  const fetching = useIsFetching();
  const mutating = useIsMutating();
  const active = fetching + mutating > 0;

  if (!active) return null;

  return (
    <LinearProgress
      aria-label="Loading"
      sx={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        zIndex: (theme) => theme.zIndex.tooltip + 2,
        height: 3,
      }}
    />
  );
}
