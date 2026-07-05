"use client";

import { Box, Typography } from "@mui/material";
import type { ReactNode } from "react";

interface MuiPageShellProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
}

export function MuiPageShell({ title, description, actions, children }: MuiPageShellProps) {
  return (
    <Box sx={{ maxWidth: 1440, mx: "auto", px: { xs: 2, sm: 3 }, py: 3 }}>
      <Box
        sx={{
          mb: 3,
          display: "flex",
          flexDirection: { xs: "column", sm: "row" },
          alignItems: { sm: "flex-start" },
          justifyContent: "space-between",
          gap: 2,
        }}
      >
        <Box>
          <Typography variant="h4" component="h1" gutterBottom={Boolean(description)}>
            {title}
          </Typography>
          {description && (
            <Typography variant="body2" color="text.secondary" maxWidth={640}>
              {description}
            </Typography>
          )}
        </Box>
        {actions && <Box sx={{ display: "flex", gap: 1, flexShrink: 0 }}>{actions}</Box>}
      </Box>
      {children}
    </Box>
  );
}
