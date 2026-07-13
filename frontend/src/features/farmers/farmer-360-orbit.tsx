"use client";

import { Box, Typography } from "@mui/material";
import type { Farmer360Section } from "@/features/farmers/api";

const SEGMENTS: {
  id: Farmer360Section;
  label: string;
  angle: number;
  color: string;
}[] = [
  { id: "overview", label: "Overview", angle: -90, color: "#2D6A4F" },
  { id: "timeline", label: "Timeline", angle: -60, color: "#40916C" },
  { id: "services", label: "Services", angle: -30, color: "#1B7F5A" },
  { id: "farming", label: "Farming", angle: 0, color: "#52B788" },
  { id: "procurements", label: "Procure", angle: 30, color: "#2D6A4F" },
  { id: "finance", label: "Finance", angle: 60, color: "#B45309" },
  { id: "ledger", label: "Ledger", angle: 90, color: "#1B4332" },
  { id: "land", label: "Land", angle: 120, color: "#40916C" },
  { id: "documents", label: "Docs", angle: 150, color: "#2D6A4F" },
  { id: "communication", label: "Comms", angle: 180, color: "#52B788" },
  { id: "analytics", label: "Analytics", angle: 210, color: "#1B7F5A" },
  { id: "actions", label: "Actions", angle: 240, color: "#B45309" },
];

interface Farmer360OrbitProps {
  farmerName: string;
  farmerCode: string;
  statusLabel: string;
  trustRating: number | null;
  active: Farmer360Section;
  onSelect: (section: Farmer360Section) => void;
}

function stars(rating: number | null): string {
  if (!rating) return "☆☆☆☆☆";
  return "★".repeat(rating) + "☆".repeat(5 - rating);
}

/** Circular 360° relationship hub — farmer at center, modules on the orbit. */
export function Farmer360Orbit({
  farmerName,
  farmerCode,
  statusLabel,
  trustRating,
  active,
  onSelect,
}: Farmer360OrbitProps) {
  const size = 340;
  const radius = 128;
  const cx = size / 2;
  const cy = size / 2;

  return (
    <Box
      sx={{
        position: "relative",
        width: { xs: 300, sm: size },
        height: { xs: 300, sm: size },
        mx: "auto",
        userSelect: "none",
      }}
      role="navigation"
      aria-label="Farmer 360 profile sections"
    >
      {/* Atmosphere rings */}
      <Box
        sx={{
          position: "absolute",
          inset: 0,
          borderRadius: "50%",
          background:
            "radial-gradient(circle at 35% 30%, rgba(82,183,136,0.35), transparent 55%), radial-gradient(circle at 70% 70%, rgba(45,106,79,0.2), transparent 50%), linear-gradient(145deg, #E8F5E9 0%, #FAFAF9 45%, #F0EDE6 100%)",
          boxShadow: "inset 0 0 40px rgba(27,67,50,0.08)",
          animation: "kfOrbitPulse 6s ease-in-out infinite",
          "@keyframes kfOrbitPulse": {
            "0%, 100%": { transform: "scale(1)" },
            "50%": { transform: "scale(1.015)" },
          },
        }}
      />
      <Box
        sx={{
          position: "absolute",
          inset: { xs: 28, sm: 32 },
          borderRadius: "50%",
          border: "1.5px dashed rgba(45,106,79,0.28)",
          animation: "kfOrbitSpin 48s linear infinite",
          "@keyframes kfOrbitSpin": {
            from: { transform: "rotate(0deg)" },
            to: { transform: "rotate(360deg)" },
          },
        }}
      />
      <Box
        sx={{
          position: "absolute",
          inset: { xs: 52, sm: 58 },
          borderRadius: "50%",
          border: "1px solid rgba(45,106,79,0.12)",
        }}
      />

      {/* Center farmer node */}
      <Box
        sx={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: "translate(-50%, -50%)",
          width: { xs: 110, sm: 124 },
          height: { xs: 110, sm: 124 },
          borderRadius: "50%",
          background: "linear-gradient(160deg, #1B4332 0%, #2D6A4F 55%, #40916C 100%)",
          color: "#fff",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          px: 1.5,
          boxShadow: "0 12px 28px rgba(27,67,50,0.35)",
          zIndex: 2,
          animation: "kfCenterIn 0.7s ease-out",
          "@keyframes kfCenterIn": {
            from: { opacity: 0, transform: "translate(-50%, -50%) scale(0.85)" },
            to: { opacity: 1, transform: "translate(-50%, -50%) scale(1)" },
          },
        }}
      >
        <Typography sx={{ fontSize: 11, opacity: 0.8, letterSpacing: 0.6 }}>360°</Typography>
        <Typography sx={{ fontSize: { xs: 13, sm: 14 }, fontWeight: 700, lineHeight: 1.2 }}>
          {farmerName.length > 16 ? `${farmerName.slice(0, 14)}…` : farmerName}
        </Typography>
        <Typography sx={{ fontSize: 10, opacity: 0.85, mt: 0.25 }}>{farmerCode}</Typography>
        <Typography sx={{ fontSize: 10, mt: 0.5, color: "#D8F3DC" }}>{statusLabel}</Typography>
        <Typography sx={{ fontSize: 10, letterSpacing: 1, color: "#FFE08A" }}>
          {stars(trustRating)}
        </Typography>
      </Box>

      {/* Orbit nodes */}
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
              left: `calc(${(x / size) * 100}% - 28px)`,
              top: `calc(${(y / size) * 100}% - 28px)`,
              width: 56,
              height: 56,
              borderRadius: "50%",
              border: isActive ? `2.5px solid ${seg.color}` : "1.5px solid rgba(45,106,79,0.2)",
              bgcolor: isActive ? seg.color : "rgba(255,255,255,0.92)",
              color: isActive ? "#fff" : "#1B4332",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 3,
              boxShadow: isActive
                ? `0 8px 20px ${seg.color}55`
                : "0 4px 12px rgba(27,67,50,0.12)",
              transition: "transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease",
              animation: `kfNodeIn 0.5s ease-out ${index * 0.04}s both`,
              "@keyframes kfNodeIn": {
                from: { opacity: 0, transform: "scale(0.6)" },
                to: { opacity: 1, transform: "scale(1)" },
              },
              "&:hover": {
                transform: "scale(1.08)",
                bgcolor: isActive ? seg.color : "#E8F5E9",
              },
              "&:focus-visible": {
                outline: `2px solid ${seg.color}`,
                outlineOffset: 3,
              },
            }}
          >
            <Typography sx={{ fontSize: 10, fontWeight: 700, lineHeight: 1.1, px: 0.5 }}>
              {seg.label}
            </Typography>
          </Box>
        );
      })}
    </Box>
  );
}

export const FARMER_360_SEGMENTS = SEGMENTS;
