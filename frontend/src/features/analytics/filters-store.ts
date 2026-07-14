import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { AnalyticsFilterState } from "./types";

interface AnalyticsFiltersState {
  filters: AnalyticsFilterState;
  savedViews: Record<string, AnalyticsFilterState>;
  setPreset: (preset: string) => void;
  setFilters: (patch: Partial<AnalyticsFilterState>) => void;
  resetFilters: () => void;
  saveView: (name: string) => void;
  loadView: (name: string) => void;
}

const defaultFilters: AnalyticsFilterState = {
  preset: "30d",
  date_from: null,
  date_to: null,
  village_id: null,
  crop_type_id: null,
  farmer_id: null,
  buyer_id: null,
  asset_id: null,
  season: null,
};

export const useAnalyticsFiltersStore = create<AnalyticsFiltersState>()(
  persist(
    (set, get) => ({
      filters: { ...defaultFilters },
      savedViews: {},
      setPreset: (preset) =>
        set((s) => ({
          filters: {
            ...s.filters,
            preset,
            date_from: preset === "custom" ? s.filters.date_from : null,
            date_to: preset === "custom" ? s.filters.date_to : null,
          },
        })),
      setFilters: (patch) => set((s) => ({ filters: { ...s.filters, ...patch } })),
      resetFilters: () => set({ filters: { ...defaultFilters } }),
      saveView: (name) =>
        set((s) => ({
          savedViews: { ...s.savedViews, [name]: { ...s.filters } },
        })),
      loadView: (name) => {
        const view = get().savedViews[name];
        if (view) set({ filters: { ...view } });
      },
    }),
    { name: "krishi-analytics-filters" },
  ),
);
