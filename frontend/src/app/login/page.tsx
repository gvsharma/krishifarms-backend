"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  IconButton,
  InputAdornment,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import { Fraunces } from "next/font/google";
import { loginWithPassword } from "@/features/auth/api";
import { clearSignedOutFlag, wasExplicitlySignedOut } from "@/features/auth/session";
import { getAccessToken } from "@/lib/api/client";
import { ROUTES, SITE_NAME } from "@/constants/routes";

const brandDisplay = Fraunces({
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  display: "swap",
});

/**
 * Split-screen login — Dribbble farm-SaaS inspiration (brand plane + calm form).
 * Canopia greens only; no purple / cream / card-heavy chrome.
 */
export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [checkingSession, setCheckingSession] = useState(true);
  const [entered, setEntered] = useState(false);

  useEffect(() => {
    if (getAccessToken() && !wasExplicitlySignedOut()) {
      router.replace(ROUTES.dashboard);
      return;
    }
    setCheckingSession(false);
    const id = window.requestAnimationFrame(() => setEntered(true));
    return () => window.cancelAnimationFrame(id);
  }, [router]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      clearSignedOutFlag();
      await loginWithPassword(email.trim(), password);
      router.replace(ROUTES.dashboard);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Login failed";
      setError(message);
    } finally {
      setSubmitting(false);
    }
  };

  if (checkingSession) {
    return (
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          bgcolor: "#F4F7F0",
        }}
      >
        <CircularProgress size={32} sx={{ color: "#2D6A4F" }} />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "grid",
        gridTemplateColumns: { xs: "1fr", md: "1.05fr 0.95fr" },
        bgcolor: "#F4F7F0",
      }}
    >
      {/* Brand plane — full-bleed on the left */}
      <Box
        sx={{
          position: "relative",
          overflow: "hidden",
          minHeight: { xs: 220, md: "100vh" },
          color: "#F4F7F0",
          background: `
            radial-gradient(ellipse 80% 60% at 20% 20%, rgba(82, 183, 136, 0.35), transparent 55%),
            radial-gradient(ellipse 70% 50% at 85% 75%, rgba(42, 157, 143, 0.28), transparent 50%),
            linear-gradient(155deg, #0F2E1F 0%, #1B4332 48%, #2D6A4F 100%)
          `,
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          px: { xs: 3, md: 7 },
          py: { xs: 4, md: 7 },
          opacity: entered ? 1 : 0,
          transform: entered ? "translateX(0)" : "translateX(-12px)",
          transition: "opacity 500ms cubic-bezier(0.22, 1, 0.36, 1), transform 500ms cubic-bezier(0.22, 1, 0.36, 1)",
        }}
      >
        {/* Soft field lines */}
        <Box
          aria-hidden
          sx={{
            position: "absolute",
            inset: 0,
            opacity: 0.14,
            backgroundImage: `
              repeating-linear-gradient(
                -12deg,
                transparent,
                transparent 28px,
                rgba(255,255,255,0.35) 28px,
                rgba(255,255,255,0.35) 29px
              )
            `,
            pointerEvents: "none",
          }}
        />

        <Typography
          className={brandDisplay.className}
          sx={{
            position: "relative",
            fontWeight: 600,
            fontSize: { xs: "1.35rem", md: "1.5rem" },
            letterSpacing: "-0.02em",
            zIndex: 1,
          }}
        >
          {SITE_NAME}
        </Typography>

        <Stack spacing={2} sx={{ position: "relative", zIndex: 1, maxWidth: 440, mt: { xs: 3, md: 0 } }}>
          <Typography
            className={brandDisplay.className}
            component="h1"
            sx={{
              fontWeight: 600,
              fontSize: { xs: "2rem", sm: "2.5rem", md: "3.25rem" },
              lineHeight: 1.08,
              letterSpacing: "-0.03em",
            }}
          >
            Field operations,
            <Box component="span" sx={{ display: "block", color: "#B7E4C7" }}>
              calmly in control.
            </Box>
          </Typography>
          <Typography
            sx={{
              color: "rgba(244, 247, 240, 0.78)",
              fontSize: { xs: "0.95rem", md: "1.05rem" },
              lineHeight: 1.55,
              maxWidth: 380,
            }}
          >
            Sign in to manage procurement, farmers, and finance for your farm network.
          </Typography>
        </Stack>

        <Typography
          variant="caption"
          sx={{
            position: "relative",
            zIndex: 1,
            color: "rgba(244, 247, 240, 0.55)",
            letterSpacing: "0.04em",
            textTransform: "uppercase",
            display: { xs: "none", md: "block" },
          }}
        >
          Bhairkhanpally · Telangana
        </Typography>
      </Box>

      {/* Form plane */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          px: { xs: 3, sm: 5 },
          py: { xs: 5, md: 7 },
          opacity: entered ? 1 : 0,
          transform: entered ? "translateY(0)" : "translateY(16px)",
          transition:
            "opacity 550ms 80ms cubic-bezier(0.22, 1, 0.36, 1), transform 550ms 80ms cubic-bezier(0.22, 1, 0.36, 1)",
        }}
      >
        <Box sx={{ width: "100%", maxWidth: 400 }}>
          <Stack spacing={1} sx={{ mb: 4 }}>
            <Typography
              variant="overline"
              sx={{ color: "#2D6A4F", letterSpacing: "0.12em", fontWeight: 600 }}
            >
              Welcome back
            </Typography>
            <Typography
              className={brandDisplay.className}
              variant="h4"
              sx={{ fontWeight: 600, color: "#1A1F16", letterSpacing: "-0.02em" }}
            >
              Sign in
            </Typography>
            <Typography variant="body2" sx={{ color: "#5C6B5E" }}>
              Use your organization email and password.
            </Typography>
          </Stack>

          <Box component="form" onSubmit={(e) => void handleSubmit(e)} noValidate>
            <Stack spacing={2.75}>
              {error && (
                <Alert
                  severity="error"
                  sx={{
                    borderRadius: 2.5,
                    bgcolor: "rgba(186, 26, 26, 0.06)",
                    border: "1px solid rgba(186, 26, 26, 0.18)",
                  }}
                >
                  {error}
                </Alert>
              )}

              <Stack spacing={1}>
                <Typography
                  component="label"
                  htmlFor="login-email"
                  sx={{ fontSize: 13, fontWeight: 600, color: "#1B4332", letterSpacing: "0.01em" }}
                >
                  Email
                </Typography>
                <TextField
                  id="login-email"
                  type="email"
                  autoComplete="email"
                  autoFocus
                  required
                  fullWidth
                  hiddenLabel
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={submitting}
                  placeholder="you@company.com"
                  sx={fieldSx}
                />
              </Stack>

              <Stack spacing={1}>
                <Typography
                  component="label"
                  htmlFor="login-password"
                  sx={{ fontSize: 13, fontWeight: 600, color: "#1B4332", letterSpacing: "0.01em" }}
                >
                  Password
                </Typography>
                <TextField
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  fullWidth
                  hiddenLabel
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={submitting}
                  placeholder="••••••••"
                  sx={fieldSx}
                  slotProps={{
                    input: {
                      endAdornment: (
                        <InputAdornment position="end">
                          <IconButton
                            aria-label={showPassword ? "Hide password" : "Show password"}
                            onClick={() => setShowPassword((v) => !v)}
                            edge="end"
                            disabled={submitting}
                            size="small"
                            sx={{ color: "#5C6B5E", mr: 0.5 }}
                          >
                            {showPassword ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
                          </IconButton>
                        </InputAdornment>
                      ),
                    },
                  }}
                />
              </Stack>

              <Button
                type="submit"
                variant="contained"
                size="large"
                fullWidth
                disabled={submitting || !email.trim() || !password}
                sx={{
                  mt: 0.5,
                  height: 52,
                  borderRadius: 999,
                  fontWeight: 600,
                  fontSize: "0.98rem",
                  textTransform: "none",
                  letterSpacing: "0.01em",
                  bgcolor: "#1B4332",
                  boxShadow: "0 12px 28px rgba(27, 67, 50, 0.25)",
                  transition: "transform 180ms ease, box-shadow 180ms ease, background-color 180ms ease",
                  "&:hover": {
                    bgcolor: "#2D6A4F",
                    boxShadow: "0 16px 34px rgba(27, 67, 50, 0.32)",
                    transform: "translateY(-1px)",
                  },
                  "&:active": {
                    transform: "translateY(0)",
                  },
                  "&.Mui-disabled": {
                    bgcolor: "rgba(27, 67, 50, 0.35)",
                    color: "#fff",
                  },
                }}
              >
                {submitting ? (
                  <Stack direction="row" spacing={1.5} alignItems="center">
                    <CircularProgress size={18} sx={{ color: "#fff" }} />
                    <span>Signing in…</span>
                  </Stack>
                ) : (
                  "Sign in"
                )}
              </Button>
            </Stack>
          </Box>

          <Typography
            variant="caption"
            sx={{ display: "block", mt: 4, color: "#5C6B5E", textAlign: "center" }}
          >
            Access is provisioned by your KrishiFarms administrator.
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}

const fieldSx = {
  "& .MuiOutlinedInput-root": {
    minHeight: 52,
    borderRadius: 3,
    bgcolor: "#FFFFFF",
    transition: "box-shadow 180ms ease, border-color 180ms ease, background-color 180ms ease",
    "& fieldset": {
      borderColor: "rgba(27, 67, 50, 0.14)",
      borderWidth: 1.5,
    },
    "&:hover": {
      bgcolor: "#FBFDFA",
      "& fieldset": {
        borderColor: "rgba(45, 106, 79, 0.45)",
      },
    },
    "&.Mui-focused": {
      bgcolor: "#FFFFFF",
      boxShadow: "0 0 0 4px rgba(45, 106, 79, 0.14)",
      "& fieldset": {
        borderColor: "#2D6A4F",
        borderWidth: 1.5,
      },
    },
  },
  "& .MuiOutlinedInput-input": {
    py: 1.6,
    px: 1.75,
    fontSize: "0.98rem",
    color: "#1A1F16",
    "&::placeholder": {
      color: "#8A978C",
      opacity: 1,
    },
  },
} as const;
