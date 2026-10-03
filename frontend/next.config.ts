import type { NextConfig } from "next";

const API_V1_PREFIX = "/api/v1";

const isVercel = Boolean(process.env.VERCEL);
const localhostApiDefault = "http://localhost:8080/api/v1";

function isLocalApiBase(value: string | undefined): boolean {
  if (!value) return true;
  return value === localhostApiDefault || value.startsWith("http://localhost");
}

const publicApiBase = (() => {
  const raw = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (isVercel && isLocalApiBase(raw)) {
    return API_V1_PREFIX;
  }
  return raw || localhostApiDefault;
})();

const apiProxyTarget = (() => {
  const raw = process.env.API_PROXY_TARGET?.replace(/\/$/, "");
  // No hardcoded fallback: the EC2 public IP is dynamic (no Elastic IP).
  // Set API_PROXY_TARGET (Vercel dashboard or build env) — see
  // docs/deploy/DYNAMIC_IP.md. Without it, /api/v1 rewrites are disabled.
  return raw ?? "";
})();

if (isVercel && publicApiBase.startsWith("http://")) {
  throw new Error(
    "NEXT_PUBLIC_API_BASE_URL must not be plain HTTP on Vercel. " +
      "Use NEXT_PUBLIC_API_BASE_URL=/api/v1 and API_PROXY_TARGET=http://<ec2-public-ip>:8082 " +
      "(current IP: bash deploy/scripts/resolve-ec2-ip.sh — see docs/deploy/DYNAMIC_IP.md).",
  );
}

const nextConfig: NextConfig = {
  async rewrites() {
    if (!apiProxyTarget) return [];
    return [
      {
        source: `${API_V1_PREFIX}/:path*`,
        destination: `${apiProxyTarget}${API_V1_PREFIX}/:path*`,
      },
    ];
  },
};

export default nextConfig;
