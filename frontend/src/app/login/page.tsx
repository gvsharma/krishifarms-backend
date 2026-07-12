"use client";

import { useEffect, useId, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Divider,
  Stack,
  Typography,
} from "@mui/material";
import Visibility from "@mui/icons-material/Visibility";
import VisibilityOff from "@mui/icons-material/VisibilityOff";
import { isEmailIdentifier, loginWithPassword } from "@/features/auth/api";
import { clearSignedOutFlag, wasExplicitlySignedOut } from "@/features/auth/session";
import { getAccessToken } from "@/lib/api/client";
import { ROUTES, SITE_NAME } from "@/constants/routes";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

/** Login field: 54px / 16px radius, soft border + clear focus — no Material motion. */
const loginFieldClassName = cn(
  "h-[54px] rounded-2xl border border-[#E5E7EB] bg-white px-4 py-3.5 text-base leading-normal text-[#111827] shadow-none",
  "placeholder:text-[#9CA3AF]",
  "transition-none",
  "hover:border-[#D1D5DB]",
  "focus-visible:border-[#111827] focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-[#111827]/12 focus-visible:ring-offset-0",
  "disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:border-[#E5E7EB]",
);

const fieldLabelClassName = "mb-2 block text-sm font-medium leading-none text-[#374151]";

function identifierLooksValid(value: string): boolean {
  const trimmed = value.trim();
  if (!trimmed) return false;
  if (isEmailIdentifier(trimmed)) return trimmed.includes("@") && !trimmed.startsWith("@");
  const digits = trimmed.replace(/\D/g, "");
  return digits.length >= 10;
}

/** Phone-first password sign-in (email OR mobile) + OTP stub. */
export default function LoginPage() {
  const router = useRouter();
  const identifierId = useId();
  const passwordId = useId();
  const errorId = useId();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    if (getAccessToken() && !wasExplicitlySignedOut()) {
      router.replace(ROUTES.dashboard);
      return;
    }
    setCheckingSession(false);
  }, [router]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    if (!identifierLooksValid(identifier)) {
      setError("Enter a valid phone number (10+ digits) or email");
      return;
    }
    setSubmitting(true);
    try {
      clearSignedOutFlag();
      await loginWithPassword(identifier, password);
      router.replace(ROUTES.dashboard);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  };

  if (checkingSession) {
    return (
      <Box sx={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
        <CircularProgress size={28} />
      </Box>
    );
  }

  const canSubmit = identifierLooksValid(identifier) && password.length >= 8 && !submitting;

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        px: 2,
        bgcolor: "#f8faf8",
      }}
    >
      <Box
        sx={{
          width: "100%",
          maxWidth: 450,
          bgcolor: "#fff",
          border: "1px solid #dadce0",
          borderRadius: 3,
          px: { xs: 3, sm: 5 },
          py: { xs: 4, sm: 5 },
        }}
      >
        <Stack spacing={1} alignItems="center" sx={{ mb: 3 }}>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: "50%",
              bgcolor: "primary.main",
              color: "#fff",
              display: "grid",
              placeItems: "center",
              fontWeight: 700,
              fontSize: 14,
            }}
            aria-hidden
          >
            KF
          </Box>
          <Typography variant="h5" fontWeight={400} component="h1">
            Sign in
          </Typography>
          <Typography variant="body2" color="text.secondary">
            to continue to {SITE_NAME}
          </Typography>
        </Stack>

        <Box component="form" onSubmit={(e) => void handleSubmit(e)} noValidate>
          <Stack spacing={2.5}>
            {error && (
              <Alert severity="error" id={errorId} role="alert">
                {error}
              </Alert>
            )}

            <div>
              <label htmlFor={identifierId} className={fieldLabelClassName}>
                Phone or email
              </label>
              <Input
                id={identifierId}
                name="identifier"
                type="text"
                inputMode="tel"
                autoComplete="username"
                autoFocus
                required
                placeholder="10-digit phone or email"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                disabled={submitting}
                aria-invalid={error ? true : undefined}
                aria-describedby={error ? errorId : undefined}
                className={loginFieldClassName}
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.75, display: "block" }}>
                Prefer phone (10+ digits, +91 optional) — same password as email login
              </Typography>
            </div>

            <div>
              <label htmlFor={passwordId} className={fieldLabelClassName}>
                Password
              </label>
              <div
                className={cn(
                  loginFieldClassName,
                  "flex items-center gap-0 p-0 focus-within:border-[#111827] focus-within:ring-[3px] focus-within:ring-[#111827]/12",
                )}
              >
                <Input
                  id={passwordId}
                  name="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={submitting}
                  aria-invalid={error ? true : undefined}
                  aria-describedby={error ? errorId : undefined}
                  className="h-full min-h-0 flex-1 border-0 bg-transparent px-4 py-3.5 shadow-none focus-visible:border-transparent focus-visible:ring-0"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  disabled={submitting}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  aria-pressed={showPassword}
                  className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-[#6B7280] transition-none hover:bg-[#F3F4F6] hover:text-[#111827] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#111827]/20 disabled:opacity-50"
                >
                  {showPassword ? (
                    <VisibilityOff fontSize="small" aria-hidden />
                  ) : (
                    <Visibility fontSize="small" aria-hidden />
                  )}
                </button>
              </div>
            </div>

            <Box sx={{ display: "flex", justifyContent: "flex-end", pt: 1 }}>
              <Button
                type="submit"
                variant="contained"
                disableElevation
                disabled={!canSubmit}
                sx={{
                  minWidth: 96,
                  minHeight: 40,
                  textTransform: "none",
                  fontWeight: 600,
                  transition: "none",
                }}
              >
                {submitting ? <CircularProgress size={18} color="inherit" /> : "Sign in"}
              </Button>
            </Box>

            <Divider sx={{ my: 0.5 }}>
              <Typography variant="caption" color="text.secondary">
                or
              </Typography>
            </Divider>

            <Button
              type="button"
              variant="outlined"
              fullWidth
              disabled
              aria-disabled
              title="Firebase Phone OTP will call POST /auth/firebase-login — see docs/modules/FIREBASE_OTP.md"
              sx={{
                minHeight: 44,
                textTransform: "none",
                fontWeight: 500,
                borderColor: "#dadce0",
                color: "text.secondary",
              }}
            >
              Login with OTP (coming soon)
            </Button>
          </Stack>
        </Box>
      </Box>
    </Box>
  );
}
