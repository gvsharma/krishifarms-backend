/** Procurement draft extras stored in notes until API columns exist. */

export const PAYMENT_TERM_OPTIONS = [
  { value: "one_week", label: "One Week" },
  { value: "10_days", label: "10 Days" },
  { value: "2_weeks", label: "2 Weeks" },
  { value: "20_days", label: "20 Days" },
  { value: "custom", label: "Custom" },
] as const;

export type PaymentTermValue = (typeof PAYMENT_TERM_OPTIONS)[number]["value"];

export interface ProcurementDraftExtras {
  buyer_id?: string;
  buyer_name?: string;
  payment_terms?: PaymentTermValue | "";
  payment_terms_custom?: string;
  moisture_pct?: string;
  rate_per_quintal?: string;
}

const MARKER_START = "[kf:proc]";
const MARKER_END = "[/kf:proc]";

export function mergeProcurementExtrasIntoNotes(
  freeNotes: string,
  extras: ProcurementDraftExtras,
): string | null {
  const payload: ProcurementDraftExtras = {};
  if (extras.buyer_id) payload.buyer_id = extras.buyer_id;
  if (extras.buyer_name) payload.buyer_name = extras.buyer_name;
  if (extras.payment_terms) payload.payment_terms = extras.payment_terms;
  if (extras.payment_terms_custom) payload.payment_terms_custom = extras.payment_terms_custom;
  if (extras.moisture_pct?.trim()) payload.moisture_pct = extras.moisture_pct.trim();
  if (extras.rate_per_quintal?.trim()) payload.rate_per_quintal = extras.rate_per_quintal.trim();

  const free = freeNotes.trim();
  if (Object.keys(payload).length === 0) return free || null;
  const block = `${MARKER_START}${JSON.stringify(payload)}${MARKER_END}`;
  return free ? `${block}\n${free}` : block;
}

export function parseProcurementExtrasFromNotes(notes: string | null | undefined): {
  extras: ProcurementDraftExtras | null;
  freeNotes: string;
} {
  if (!notes) return { extras: null, freeNotes: "" };
  const start = notes.indexOf(MARKER_START);
  const end = notes.indexOf(MARKER_END);
  if (start === -1 || end === -1 || end <= start) {
    return { extras: null, freeNotes: notes };
  }
  const json = notes.slice(start + MARKER_START.length, end).trim();
  const freeNotes = `${notes.slice(0, start)}${notes.slice(end + MARKER_END.length)}`.trim();
  try {
    const extras = JSON.parse(json) as ProcurementDraftExtras;
    return { extras, freeNotes };
  } catch {
    return { extras: null, freeNotes: notes };
  }
}

export function paymentTermsLabel(
  terms: string | null | undefined,
  custom?: string | null,
): string | null {
  if (!terms) return null;
  if (terms === "custom") {
    return custom?.trim() || "Custom";
  }
  return PAYMENT_TERM_OPTIONS.find((o) => o.value === terms)?.label ?? terms;
}

/** Prefer first-class API fields; fall back to parsed [kf:proc] notes. */
export function resolveProcurementDisplayExtras(
  data: {
    buyer_name?: string | null;
    payment_terms?: string | null;
    payment_terms_custom?: string | null;
    notes?: string | null;
  },
): {
  buyerName: string | null;
  paymentTerms: string | null;
  plannedMoisturePct: string | null;
  plannedRate: string | null;
  freeNotes: string;
} {
  const { extras, freeNotes } = parseProcurementExtrasFromNotes(data.notes);
  return {
    buyerName: data.buyer_name ?? extras?.buyer_name ?? null,
    paymentTerms:
      paymentTermsLabel(data.payment_terms, data.payment_terms_custom) ??
      paymentTermsLabel(extras?.payment_terms, extras?.payment_terms_custom),
    plannedMoisturePct: extras?.moisture_pct ?? null,
    plannedRate: extras?.rate_per_quintal ?? null,
    freeNotes,
  };
}
