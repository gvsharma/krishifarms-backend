import type { ViewportSize } from "@playwright/test";

/** Named viewport presets for responsive and visual tests. */
export const VIEWPORTS = {
  desktop: { width: 1920, height: 1080 },
  laptop: { width: 1366, height: 768 },
  tablet: { width: 768, height: 1024 },
  mobilePortrait: { width: 390, height: 844 },
  mobileLandscape: { width: 844, height: 390 },
  /** @deprecated Use mobilePortrait */
  mobile: { width: 390, height: 844 },
  /** @deprecated Use mobileLandscape */
  landscape: { width: 844, height: 390 },
  /** @deprecated Use mobilePortrait */
  portrait: { width: 390, height: 844 },
} as const satisfies Record<string, ViewportSize>;

export type ViewportPreset = keyof typeof VIEWPORTS;

export function viewportPreset(name: ViewportPreset): ViewportSize {
  return VIEWPORTS[name];
}
