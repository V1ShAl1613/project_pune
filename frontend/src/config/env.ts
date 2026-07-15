export const env = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000",
  appName: process.env.NEXT_PUBLIC_APP_NAME ?? "Sentinel Fusion AI",
  appVersion: process.env.NEXT_PUBLIC_APP_VERSION ?? "1.0.0",
} as const;
