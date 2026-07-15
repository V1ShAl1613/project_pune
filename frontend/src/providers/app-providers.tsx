"use client";

import { AppQueryProvider } from "@/providers/query-provider";
import { ThemeProvider } from "@/providers/theme-provider";

export function AppProviders({ children }: { children: React.ReactNode }): React.JSX.Element {
  return (
    <AppQueryProvider>
      <ThemeProvider>{children}</ThemeProvider>
    </AppQueryProvider>
  );
}
