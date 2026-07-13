"use client";

import { Box, Typography } from "@mui/material";
import type { Village360Section } from "@/features/villages/api";

const SEGMENTS: { id: Village360Section; label: string; angle: number; color: string }[] = [
  { id: "overview", label: "Overview", angle: -90, color: "#1B4332" },
  { id: "farmers", label: "Farmers", angle: -62, color: "#2D6A4F" },
  { id: "procurements", label: "Procure", angle: -34, color: "#40916C" },
  { id: "services", label: "Services", angle: -6, color: "#52B788" },
  { id: "vehicles", label: "Vehicles", angle: 22, color: "#1B7F5A" },
  { id: "payments", label: "Payments", angle: 50, color: "#B45309" },
  { id: "finance", label: "Finance", angle: 78, color: "#2D6A4F" },
  { id: "farming", label: "Farming", angle: 106, color: "#40916C" },
  { id: "buyers", label: "Buyers", angle: 134, color: "#1B4332" },
  { id: "comments", label: "Comms", angle: 162, color: "#52B788" },
  { id: "documents", label: "Docs", angle: 190, color: "#2D6A4F" },
  { id: "analytics", label: "Analytics", angle: 218, color: "#1B7F5A" },
  { id: "timeline", label: "Timeline", angle: 246, color: "#B45309" },
];

interface Props {
  villageName: string;
  villageCode: string | null;
  status: string;
  active: Village360Section;
  onSelect: (section: Village360Section) => void;
}

/** Circular Village 360° hub — village at center, CRM modules on the orbit. */
export function Village360Orbit({ villageName, villageCode, status, active, onSelect }: Props) {
  const size = 360;
  const radius = 138;
  const cx = size / 2;
  const cy = size / 2;

  return (
    <Box
      sx={{
        position: "relative",
        width: { xs: 300, sm: size },
        height: { xs: 300, sm: size },
        mx: "auto",
      }}
      role="navigation"
      aria-label="Village 360 profile sections"
    >
      <Box
        sx={{
          position: "absolute",
          inset: 0,
          borderRadius: "50%",
          background:
            "radial-gradient(circle at 30% 28%, rgba(64,145,108,0.4), transparent 52%), radial-gradient(circle at 75% 72%, rgba(27,67,50,0.22), transparent 48%), linear-gradient(150deg, #E9F5EE 0%, #FAFAF9 50%, #F3EFE6 100%)",
          animation: "kfVPulse 7s ease-in-out infinite",
          "@keyframes kfVPulse": {
            "0%,100%": { transform: "scale(1)" },
            "50%": { transform: "scale(1.012)" },
          },
        }}
      />
      <Box
        sx={{
          position: "absolute",
          inset: 34,
          borderRadius: "50%",
          border: "1.5px dashed rgba(27,67,50,0.25)",
          animation: "kfVSpin 56s linear infinite",
          "@keyframes kfVSpin": {
            from: { transform: "rotate(0deg)" },
            to: { transform: "rotate(360deg)" },
          },
        }}
      />

      <Box
        sx={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: "translate(-50%, -50%)",
          width: { xs: 112, sm: 128 },
          height: { xs: 112, sm: 128 },
          borderRadius: "50%",
          background: "linear-gradient(155deg, #081C15 0%, #1B4332 45%, #2D6A4F 100%)",
          color: "#fff",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          px: 1.5,
          boxShadow: "0 14px 32px rgba(8,28,21,0.4)",
          zIndex: 2,
        }}
      >
        <Typography sx={{ fontSize: 11, opacity: 0.75, letterSpacing: 0.8 }}>VILLAGE 360°</Typography>
        <Typography sx={{ fontSize: 13, fontWeight: 700, lineHeight: 1.15, mt: 0.25 }}>
          {villageName.length > 18 ? `${villageName.slice(0, 16)}…` : villageName}
        </Typography>
        <Typography sx={{ fontSize: 10, opacity: 0.85 }}>{villageCode ?? "—"}</Typography>
        <Typography sx={{ fontSize: 10, color: "#95D5B2", mt: 0.35 }}>{status}</Typography>
      </Box>

      {SEGMENTS.map((seg, index) => {
        const rad = (seg.angle * Math.PI) / 180;
        const x = cx + radius * Math.cos(rad);
        const y = cy + radius * Math.sin(rad);
        const isActive = active === seg.id;
        return (
          <Box
            key={seg.id}
            component="button"
            type="button"
            onClick={() => onSelect(seg.id)}
            aria-pressed={isActive}
            aria-label={seg.label}
            sx={{
              position: "absolute",
              left: `calc(${(x / size) * 100}% - 26px)`,
              top: `calc(${(y / size) * 100}% - 26px)`,
              width: 52,
              height: 52,
              borderRadius: "50%",
              border: isActive ? `2.5px solid ${seg.color}` : "1.5px solid rgba(27,67,50,0.18)",
              bgcolor: isActive ? seg.color : "rgba(255,255,255,0.94)",
              color: isActive ? "#fff" : "#081C15",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 3,
              boxShadow: isActive ? `0 8px 18px ${seg.color}55` : "0 3px 10px rgba(8,28,21,0.1)",
              animation: `kfVNIn 0.45s ease-out ${index * 0.03}s both`,
              "@keyframes kfVNIn": {
                from: { opacity: 0, transform: "scale(0.55)" },
                to: { opacity: 1, transform: "scale(1)" },
              },
              "&:hover": { transform: "scale(1.08)" },
            }}
          >
            <Typography sx={{ fontSize: 9, fontWeight: 700, lineHeight: 1.05, px: 0.4 }}>
              {seg.label}
            </Typography>
          </Box>
        );
      })}
    </Box>
  );
}
