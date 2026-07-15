import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { ThemeMode } from "@/types/ui";

type ThemeState = {
  theme: ThemeMode;
  setTheme: (theme: ThemeMode) => void;
};

export const themeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: "system",
      setTheme: (theme) => set({ theme }),
    }),
    { name: "sentinel-theme" },
  ),
);
