/**
 * Unit tests for session recovery helpers (no path aliases).
 * Run: cd frontend && npm run test:unit
 */
import { describe, it, mock } from "node:test";
import assert from "node:assert/strict";
import {
  decideUnauthorizedRecovery,
  exchangeRefreshToken,
  isUnauthorizedStatus,
  normalizeApiPath,
  parseRefreshTokenPayload,
  shouldSkipAuthRefresh,
} from "./session-recovery.ts";

describe("normalizeApiPath", () => {
  it("keeps relative API paths", () => {
    assert.equal(normalizeApiPath("/auth/me"), "/auth/me");
    assert.equal(normalizeApiPath("auth/me"), "/auth/me");
  });

  it("strips /api/v1 prefix from absolute URLs", () => {
    assert.equal(
      normalizeApiPath("https://example.com/api/v1/auth/refresh"),
      "/auth/refresh",
    );
    assert.equal(normalizeApiPath("/api/v1/auth/me"), "/auth/me");
  });
});

describe("shouldSkipAuthRefresh", () => {
  it("skips login/refresh/logout/firebase-login", () => {
    assert.equal(shouldSkipAuthRefresh("/auth/login"), true);
    assert.equal(shouldSkipAuthRefresh("/auth/refresh"), true);
    assert.equal(shouldSkipAuthRefresh("/auth/logout"), true);
    assert.equal(shouldSkipAuthRefresh("/auth/firebase-login"), true);
    assert.equal(
      shouldSkipAuthRefresh("https://api.example/api/v1/auth/refresh"),
      true,
    );
  });

  it("does not skip authenticated endpoints", () => {
    assert.equal(shouldSkipAuthRefresh("/auth/me"), false);
    assert.equal(shouldSkipAuthRefresh("/field-services"), false);
    assert.equal(shouldSkipAuthRefresh("/farmers"), false);
  });
});

describe("unauthorized recovery decision", () => {
  it("recognizes 401 only", () => {
    assert.equal(isUnauthorizedStatus(401), true);
    assert.equal(isUnauthorizedStatus(403), false);
    assert.equal(isUnauthorizedStatus(500), false);
  });

  it("retries after successful refresh", () => {
    assert.equal(decideUnauthorizedRecovery(true), "retry");
  });

  it("logs out when refresh fails", () => {
    assert.equal(decideUnauthorizedRecovery(false), "logout");
  });
});

describe("parseRefreshTokenPayload", () => {
  it("reads API envelope", () => {
    const tokens = parseRefreshTokenPayload({
      success: true,
      data: { access_token: "a", refresh_token: "r", token_type: "bearer" },
    });
    assert.deepEqual(tokens, {
      access_token: "a",
      refresh_token: "r",
      token_type: "bearer",
    });
  });

  it("rejects incomplete payloads", () => {
    assert.equal(parseRefreshTokenPayload({ data: { access_token: "a" } }), null);
    assert.equal(parseRefreshTokenPayload(null), null);
  });
});

describe("exchangeRefreshToken", () => {
  it("returns tokens on 200 envelope", async () => {
    const fetchImpl = mock.fn(
      async (): Promise<Response> =>
        Response.json({
          success: true,
          data: { access_token: "a1", refresh_token: "r1", token_type: "bearer" },
        }),
    );

    const tokens = await exchangeRefreshToken({
      apiBase: "http://api.test/api/v1",
      refreshToken: "old",
      deviceId: "dev-1",
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    assert.deepEqual(tokens, {
      access_token: "a1",
      refresh_token: "r1",
      token_type: "bearer",
    });
    assert.equal(fetchImpl.mock.calls.length, 1);
    const call = fetchImpl.mock.calls[0];
    const url = call.arguments[0];
    const init = call.arguments[1] as RequestInit;
    assert.equal(url, "http://api.test/api/v1/auth/refresh");
    assert.equal(init.method, "POST");
  });

  it("returns null on 401", async () => {
    const fetchImpl = mock.fn(
      async (): Promise<Response> =>
        Response.json({ error: { message: "Invalid refresh token" } }, { status: 401 }),
    );

    const tokens = await exchangeRefreshToken({
      apiBase: "http://api.test/api/v1",
      refreshToken: "bad",
      deviceId: "dev-1",
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    assert.equal(tokens, null);
  });

  it("returns null on network failure", async () => {
    const fetchImpl = mock.fn(async (): Promise<Response> => {
      throw new Error("offline");
    });

    const tokens = await exchangeRefreshToken({
      apiBase: "http://api.test/api/v1",
      refreshToken: "x",
      deviceId: "dev-1",
      fetchImpl: fetchImpl as unknown as typeof fetch,
    });
    assert.equal(tokens, null);
  });
});
