/** Sync per-bag weight rows when bag count changes. */

export function resizeBagWeights(current: string[], bagCount: number, defaultKg = "50"): string[] {
  const n = Math.max(0, Math.floor(bagCount));
  if (n === 0) return [];
  const next = current.slice(0, n);
  while (next.length < n) {
    next.push(defaultKg);
  }
  return next;
}

export function parseBagWeights(weights: string[]): number[] {
  return weights.map((w) => Number(w)).filter((n) => Number.isFinite(n) && n > 0);
}

export function bagWeightsValid(weights: string[], bagCount: number): boolean {
  if (bagCount <= 0) return false;
  if (weights.length !== bagCount) return false;
  return weights.every((w) => {
    const n = Number(w);
    return Number.isFinite(n) && n > 0;
  });
}

export function sumBagWeightsKg(weights: string[]): number {
  return weights.reduce((sum, w) => {
    const n = Number(w);
    return sum + (Number.isFinite(n) && n > 0 ? n : 0);
  }, 0);
}

export function averageBagWeight(weights: string[]): number | null {
  const parsed = parseBagWeights(weights);
  if (parsed.length === 0) return null;
  return parsed.reduce((a, b) => a + b, 0) / parsed.length;
}
