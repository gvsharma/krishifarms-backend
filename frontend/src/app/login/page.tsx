"use client";

import { useEffect, useId, useState, type CSSProperties } from "react";
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
import { Eye, EyeOff } from "lucide-react";
import { isEmailIdentifier, loginWithPassword } from "@/features/auth/api";
import { clearSignedOutFlag, wasExplicitlySignedOut } from "@/features/auth/session";
import { getAccessToken } from "@/lib/api/client";
import { ROUTES, SITE_NAME } from "@/constants/routes";
import { isValidIndianMobile } from "@/lib/validation/phone";
import { useTranslation } from "@/i18n/use-translation";
import type { AppLocale } from "@/i18n/messages";
import { useLocaleStore } from "@/stores/locale-store";
import { cn } from "@/lib/utils";
import { ApiHealthBanner } from "@/components/ui/api-health-banner";

/**
 * Login fields use inline border styles — Tailwind `border-*` width utilities are
 * ineffective here when MUI CSS layers omit preflight `border-style: solid`, which
 * made the password wrapper invisible and left the eye toggle with a native button chrome.
 */
const fieldShellStyle: CSSProperties = {
  border: "1px solid #E5E7EB",
  backgroundColor: "#ffffff",
  colorScheme: "light",
};

const fieldLabelClassName = "mb-2 block text-sm font-medium leading-none text-[#374151]";

const fieldInputClassName = cn(
  "h-full w-full min-w-0 border-0 bg-transparent px-4 text-base leading-normal text-[#111827]",
  "placeholder:text-[#9CA3AF]",
  "outline-none ring-0 focus:outline-none focus-visible:outline-none",
  "disabled:cursor-not-allowed disabled:opacity-60",
);

function identifierLooksValid(value: string): boolean {
  const trimmed = value.trim();
  if (!trimmed) return false;
  if (isEmailIdentifier(trimmed)) return trimmed.includes("@") && !trimmed.startsWith("@");
  return isValidIndianMobile(trimmed);
}

/** Phone-first password sign-in (email OR mobile) + OTP stub. */
export default function LoginPage() {
  const router = useRouter();
  const { t } = useTranslation();
  const setLocale = useLocaleStore((s) => s.setLocale);
  const locale = useLocaleStore((s) => s.locale);
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
      setError(t("auth.invalidIdentifier"));
      return;
    }
    setSubmitting(true);
    try {
      clearSignedOutFlag();
      await loginWithPassword(identifier, password);
      router.replace(ROUTES.dashboard);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("auth.loginFailed"));
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
    <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column", bgcolor: "#f8faf8" }}>
      <ApiHealthBanner />
      <Box
        sx={{
          flex: 1,
          display: "grid",
          placeItems: "center",
          px: 2,
          colorScheme: "light",
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
          colorScheme: "light",
        }}
      >
        <Stack spacing={1} alignItems="center" sx={{ mb: 3 }}>
          <Stack direction="row" spacing={1} sx={{ alignSelf: "flex-end", mb: 1 }}>
            {(["en", "te"] as AppLocale[]).map((code) => (
              <Button
                key={code}
                size="small"
                variant={locale === code ? "contained" : "text"}
                onClick={() => setLocale(code)}
                sx={{ minWidth: 56, textTransform: "none" }}
              >
                {code === "en" ? "EN" : "తె"}
              </Button>
            ))}
          </Stack>
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
            {t("auth.signIn")}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {t("auth.signInTo", { site: SITE_NAME })}
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
                {t("auth.phoneOrEmail")}
              </label>
              <div
                className="flex h-[54px] items-center overflow-hidden rounded-2xl transition-[border-color,box-shadow] focus-within:border-[#111827] focus-within:shadow-[0_0_0_3px_rgba(17,24,39,0.12)]"
                style={fieldShellStyle}
              >
                <input
                  id={identifierId}
                  name="identifier"
                  type="text"
                  inputMode="tel"
                  autoComplete="username"
                  autoFocus
                  required
                  placeholder={t("auth.phoneOrEmailPlaceholder")}
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  disabled={submitting}
                  aria-invalid={error ? true : undefined}
                  aria-describedby={error ? errorId : undefined}
                  className={fieldInputClassName}
                />
              </div>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.75, display: "block" }}>
                {t("auth.phoneHint")}
              </Typography>
            </div>

            <div>
              <label htmlFor={passwordId} className={fieldLabelClassName}>
                {t("auth.password")}
              </label>
              <div
                className="flex h-[54px] items-center overflow-hidden rounded-2xl transition-[border-color,box-shadow] focus-within:border-[#111827] focus-within:shadow-[0_0_0_3px_rgba(17,24,39,0.12)]"
                style={fieldShellStyle}
              >
                <input
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
                  className={cn(fieldInputClassName, "pr-2")}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  disabled={submitting}
                  aria-label={showPassword ? t("auth.hidePassword") : t("auth.showPassword")}
                  aria-pressed={showPassword}
                  className={cn(
                    "mr-1.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl",
                    "border-0 bg-transparent text-[#6B7280]",
                    "hover:bg-[#F3F4F6] hover:text-[#111827]",
                    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#111827]/20",
                    "disabled:opacity-50",
                  )}
                  style={{ border: "none", background: "transparent", appearance: "none" }}
                >
                  {showPassword ? (
                    <EyeOff className="h-[18px] w-[18px]" strokeWidth={1.75} aria-hidden />
                  ) : (
                    <Eye className="h-[18px] w-[18px]" strokeWidth={1.75} aria-hidden />
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
                {submitting ? <CircularProgress size={18} color="inherit" /> : t("auth.signIn")}
              </Button>
            </Box>

            <Divider sx={{ my: 0.5 }}>
              <Typography variant="caption" color="text.secondary">
                {t("common.or")}
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
              {t("auth.otpComingSoon")}
            </Button>
          </Stack>
        </Box>
      </Box>
      </Box>
    </Box>
  );
}
