/** Vehicle-type-specific work details stored in field-service comments. */

export const CULTIVATION_STAGE_OPTIONS = [
  { value: "land_preparation", label: "Land preparation" },
  { value: "sowing", label: "Sowing" },
  { value: "intercultivation", label: "Intercultivation" },
  { value: "weeding", label: "Weeding" },
  { value: "harvesting", label: "Harvesting" },
  { value: "other", label: "Other" },
] as const;

export const TROLLEY_PURPOSE_OPTIONS = [
  { value: "grain_haul", label: "Grain haul" },
  { value: "fertilizer", label: "Fertilizer" },
  { value: "seed", label: "Seed" },
  { value: "soil", label: "Soil" },
  { value: "other", label: "Other" },
] as const;

export const TROLLEY_MATERIAL_OPTIONS = [
  { value: "paddy", label: "Paddy" },
  { value: "corn", label: "Corn" },
  { value: "fertilizer", label: "Fertilizer" },
  { value: "soil", label: "Soil" },
  { value: "bags", label: "Bags" },
  { value: "other", label: "Other" },
] as const;

export const LOCALITY_OPTIONS = [
  { value: "local", label: "Local" },
  { value: "non_local", label: "Non-local" },
] as const;

export const GOODS_TYPE_OPTIONS = [
  { value: "grain", label: "Grain" },
  { value: "fertilizer", label: "Fertilizer" },
  { value: "seeds", label: "Seeds" },
  { value: "tools", label: "Tools" },
  { value: "other", label: "Other" },
] as const;

export const SPRAY_TYPE_OPTIONS = [
  { value: "pesticide", label: "Pesticide" },
  { value: "fertilizer", label: "Fertilizer" },
  { value: "growth_regulator", label: "Growth regulator" },
  { value: "other", label: "Other" },
] as const;

export interface VehicleWorkDetails {
  profile: "tractor" | "trolley" | "bolero" | "dcm" | "pump" | "drone" | "baler";
  // Tractor / implements / harvester
  crop_code?: string;
  crop_name?: string;
  area_acres?: string;
  cultivation_stage?: string;
  // Trolley / baler
  trips?: string;
  bale_count?: string;
  purpose?: string;
  material?: string;
  // Bolero
  locality?: string;
  distance_km?: string;
  weight_kg?: string;
  goods_type?: string;
  // DCM
  tonnes?: string;
  loading_point?: string;
  unloading_point?: string;
  // Pump
  litres?: string;
  // Drone
  spray_type?: string;
}

const MARKER_START = "[kf:work]";
const MARKER_END = "[/kf:work]";

export function parseWorkDetailsFromComments(comments: string | null | undefined): {
  details: VehicleWorkDetails | null;
  freeComments: string;
} {
  if (!comments) return { details: null, freeComments: "" };
  const start = comments.indexOf(MARKER_START);
  const end = comments.indexOf(MARKER_END);
  if (start === -1 || end === -1 || end <= start) {
    return { details: null, freeComments: comments };
  }
  const json = comments.slice(start + MARKER_START.length, end).trim();
  const freeComments = `${comments.slice(0, start)}${comments.slice(end + MARKER_END.length)}`.trim();
  try {
    const details = JSON.parse(json) as VehicleWorkDetails;
    if (!details?.profile) return { details: null, freeComments: comments };
    return { details, freeComments };
  } catch {
    return { details: null, freeComments: comments };
  }
}

export function mergeWorkDetailsIntoComments(
  freeComments: string,
  details: VehicleWorkDetails | null,
): string | null {
  const free = freeComments.trim();
  if (!details) return free || null;
  const block = `${MARKER_START}${JSON.stringify(details)}${MARKER_END}`;
  return free ? `${block}\n${free}` : block;
}

/** Touch-friendly MUI TextField defaults for field ops forms. */
export const TOUCH_FIELD_SX = {
  "& .MuiInputBase-root": { minHeight: 52 },
  "& .MuiSelect-select": { py: 1.5 },
} as const;
