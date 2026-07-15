import { create } from "zustand";
import { persist } from "zustand/middleware";

type PreferenceState = {
  language: string;
  timezone: string;
  density: "comfortable" | "compact";
  organizationId: string | null;
  setLanguage: (language: string) => void;
  setTimezone: (timezone: string) => void;
  setDensity: (density: "comfortable" | "compact") => void;
  setOrganizationId: (organizationId: string | null) => void;
};

export const preferenceStore = create<PreferenceState>()(
  persist(
    (set) => ({
      language: "en",
      timezone: "UTC",
      density: "comfortable",
      organizationId: null,
      setLanguage: (language) => set({ language }),
      setTimezone: (timezone) => set({ timezone }),
      setDensity: (density) => set({ density }),
      setOrganizationId: (organizationId) => set({ organizationId }),
    }),
    { name: "sentinel-preferences" },
  ),
);
