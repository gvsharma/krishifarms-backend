"use client";

import { TableContainer, type TableContainerProps } from "@mui/material";
import type { ReactNode } from "react";

/** Horizontal scroll wrapper for wide tables on mobile. */
export function ResponsiveTable({
  children,
  ...props
}: TableContainerProps & { children: ReactNode }) {
  return (
    <TableContainer
      {...props}
      sx={{
        overflowX: "auto",
        WebkitOverflowScrolling: "touch",
        ...props.sx,
      }}
    >
      {children}
    </TableContainer>
  );
}
