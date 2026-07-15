"use client";

import { useEffect } from "react";

import { themeStore } from "@/store/theme-store";

export function ThemeProvider({ children }: { children: React.ReactNode }): React.JSX.Element {
  const theme = themeStore((state) => state.theme);

  useEffect(() => {
    const root = document.documentElement;
    const systemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const resolvedTheme = theme === "system" ? (systemDark ? "dark" : "light") : theme;
    root.dataset.theme = resolvedTheme;
    root.classList.toggle("dark", resolvedTheme === "dark");
  }, [theme]);

  return <>{children}</>;
}
