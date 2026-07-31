"use client";

import { Backdrop, CircularProgress, LinearProgress } from "@mui/material";
import { useIsFetching, useIsMutating } from "@tanstack/react-query";

/** Top-of-screen progress while fetching; full-screen backdrop during mutations. */
export function GlobalLoadingBar() {
  const fetching = useIsFetching();
  const mutating = useIsMutating();
  const fetchActive = fetching > 0;
  const mutateActive = mutating > 0;

  return (
    <>
      {fetchActive && !mutateActive && (
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
      )}
      <Backdrop
        open={mutateActive}
        sx={{
          zIndex: (theme) => theme.zIndex.modal + 1,
          color: "common.white",
        }}
      >
        <CircularProgress color="inherit" aria-label="Saving" />
      </Backdrop>
    </>
  );
}
