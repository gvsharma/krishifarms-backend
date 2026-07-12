"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Alert,
  Avatar,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { loginWithPassword } from "@/features/auth/api";
import { wasExplicitlySignedOut } from "@/features/auth/session";
import { getAccessToken } from "@/lib/api/client";
import { ROUTES, SITE_NAME } from "@/constants/routes";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
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
    setSubmitting(true);

    try {
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
        }}
      >
        <CircularProgress size={32} />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        bgcolor: "background.default",
        px: 2,
      }}
    >
      <Card sx={{ width: "100%", maxWidth: 420 }}>
        <CardContent sx={{ p: 4 }}>
          <Stack spacing={3} alignItems="center">
            <Avatar sx={{ width: 48, height: 48, bgcolor: "primary.main", fontWeight: 700 }}>
              KF
            </Avatar>
            <Stack spacing={0.5} textAlign="center">
              <Typography variant="h5" fontWeight={600}>
                Sign in to {SITE_NAME}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Farm operations CRM
              </Typography>
            </Stack>

            <Box component="form" onSubmit={(e) => void handleSubmit(e)} sx={{ width: "100%" }}>
              <Stack spacing={2}>
                {error && <Alert severity="error">{error}</Alert>}
                <TextField
                  label="Email"
                  type="email"
                  autoComplete="email"
                  required
                  fullWidth
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={submitting}
                />
                <TextField
                  label="Password"
                  type="password"
                  autoComplete="current-password"
                  required
                  fullWidth
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={submitting}
                />
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  fullWidth
                  disabled={submitting}
                >
                  {submitting ? "Signing in…" : "Sign in"}
                </Button>
              </Stack>
            </Box>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  );
}
