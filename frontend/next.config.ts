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
  if (isVercel) {
    return raw || "http://13.232.200.243";
  }
  return raw ?? "";
})();

if (isVercel && publicApiBase.startsWith("http://")) {
  throw new Error(
    "NEXT_PUBLIC_API_BASE_URL must not be plain HTTP on Vercel. " +
      "Use NEXT_PUBLIC_API_BASE_URL=/api/v1 and API_PROXY_TARGET=http://<ec2-ip>.",
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
