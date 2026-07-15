export const SESSION_COOKIE_NAME = "sentinel-session";

export function setSessionCookie(): void {
  document.cookie = `${SESSION_COOKIE_NAME}=active; path=/; sameSite=lax`;
}

export function clearSessionCookie(): void {
  document.cookie = `${SESSION_COOKIE_NAME}=; path=/; max-age=0; sameSite=lax`;
}
