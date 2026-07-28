"use client";

import {
  Alert,
  Box,
  Card,
  CardContent,
  FormControl,
  FormControlLabel,
  Radio,
  RadioGroup,
  Snackbar,
  Stack,
  Typography,
} from "@mui/material";
import { Language, Palette } from "@mui/icons-material";
import { useTheme as useNextTheme } from "next-themes";
import { useEffect, useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { updateCurrentUser } from "@/features/settings/preferences-api";
import { useTranslation } from "@/i18n/use-translation";
import type { AppLocale } from "@/i18n/messages";
import { useLocaleStore } from "@/stores/locale-store";
import { useAuth } from "@/hooks/use-auth";

type ThemeChoice = "light" | "dark" | "system";

export default function PreferencesPage() {
  const { t } = useTranslation();
  const locale = useLocaleStore((s) => s.locale);
  const setLocale = useLocaleStore((s) => s.setLocale);
  const { user, refetch } = useAuth();
  const { theme, setTheme, resolvedTheme } = useNextTheme();
  const [mounted, setMounted] = useState(false);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<{ message: string; severity: "success" | "error" } | null>(
    null,
  );

  useEffect(() => setMounted(true), []);

  const themeChoice: ThemeChoice =
    theme === "light" || theme === "dark" || theme === "system" ? theme : "system";

  const handleLocaleChange = async (next: AppLocale) => {
    if (next === locale) return;
    setLocale(next);
    setSaving(true);
    try {
      if (user) {
        await updateCurrentUser({ preferred_locale: next });
        await refetch();
      }
      setToast({ message: t("settings.saved"), severity: "success" });
    } catch {
      setToast({ message: t("settings.saveFailed"), severity: "error" });
    } finally {
      setSaving(false);
    }
  };

  const handleThemeChange = (next: ThemeChoice) => {
    setTheme(next);
    setToast({ message: t("settings.saved"), severity: "success" });
  };

  return (
    <MuiPageShell title={t("settings.preferences")} description={t("settings.preferencesDesc")}>
      <Stack spacing={2} maxWidth={560}>
        <Card>
          <CardContent>
            <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 2 }}>
              <Language color="primary" />
              <Box>
                <Typography variant="subtitle1" fontWeight={600}>
                  {t("settings.language")}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t("settings.languageDesc")}
                </Typography>
              </Box>
            </Stack>
            <FormControl component="fieldset" disabled={saving}>
              <RadioGroup
                value={locale}
                onChange={(e) => void handleLocaleChange(e.target.value as AppLocale)}
              >
                <FormControlLabel
                  value="en"
                  control={<Radio />}
                  label={t("settings.language.en")}
                  sx={{ minHeight: 48 }}
                />
                <FormControlLabel
                  value="te"
                  control={<Radio />}
                  label={t("settings.language.te")}
                  sx={{ minHeight: 48, fontFamily: "var(--font-noto-telugu), sans-serif" }}
                />
              </RadioGroup>
            </FormControl>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Stack direction="row" spacing={1.5} alignItems="center" sx={{ mb: 2 }}>
              <Palette color="primary" />
              <Box>
                <Typography variant="subtitle1" fontWeight={600}>
                  {t("settings.appearance")}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t("settings.appearanceDesc")}
                </Typography>
              </Box>
            </Stack>
            {mounted ? (
              <FormControl component="fieldset">
                <RadioGroup
                  value={themeChoice}
                  onChange={(e) => handleThemeChange(e.target.value as ThemeChoice)}
                >
                  <FormControlLabel
                    value="light"
                    control={<Radio />}
                    label={t("settings.theme.light")}
                    sx={{ minHeight: 48 }}
                  />
                  <FormControlLabel
                    value="dark"
                    control={<Radio />}
                    label={t("settings.theme.dark")}
                    sx={{ minHeight: 48 }}
                  />
                  <FormControlLabel
                    value="system"
                    control={<Radio />}
                    label={t("settings.theme.system")}
                    sx={{ minHeight: 48 }}
                  />
                </RadioGroup>
              </FormControl>
            ) : (
              <Typography variant="body2" color="text.secondary">
                {t("common.loading")}
              </Typography>
            )}
            {mounted && resolvedTheme && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: "block" }}>
                {resolvedTheme === "dark" ? t("settings.theme.dark") : t("settings.theme.light")}
              </Typography>
            )}
          </CardContent>
        </Card>
      </Stack>

      <Snackbar
        open={Boolean(toast)}
        autoHideDuration={3000}
        onClose={() => setToast(null)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        {toast ? (
          <Alert severity={toast.severity} onClose={() => setToast(null)} sx={{ width: "100%" }}>
            {toast.message}
          </Alert>
        ) : undefined}
      </Snackbar>
    </MuiPageShell>
  );
}
