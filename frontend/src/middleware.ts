import { NextRequest, NextResponse } from "next/server";

const protectedPaths = [
  "/dashboard",
  "/soc-center",
  "/alerts",
  "/cases",
  "/tenants",
  "/workspaces",
  "/intel",
  "/iocs",
  "/attack",
  "/mitre",
  "/workbench",
  "/timeline",
  "/organizations",
  "/departments",
  "/teams",
  "/users",
  "/roles",
  "/permissions",
  "/groups",
  "/invitations",
  "/sessions",
  "/apikeys",
  "/service-accounts",
  "/threat-center",
  "/sso",
  "/mfa",
  "/audit",
  "/profile",
  "/settings",
  "/administration",
];

export function middleware(request: NextRequest): NextResponse {
  const { pathname } = request.nextUrl;
  const isProtected = protectedPaths.some((path) => pathname.startsWith(path));
  if (!isProtected) {
    return NextResponse.next();
  }
  const sessionCookie = request.cookies.get("sentinel-session");
  if (sessionCookie?.value) {
    return NextResponse.next();
  }
  const url = request.nextUrl.clone();
  url.pathname = "/session-expired";
  return NextResponse.redirect(url);
}

export const config = {
  matcher: ["/dashboard/:path*", "/soc-center/:path*", "/alerts/:path*", "/cases/:path*", "/tenants/:path*", "/workspaces/:path*", "/organizations/:path*", "/departments/:path*", "/teams/:path*", "/users/:path*", "/roles/:path*", "/permissions/:path*", "/groups/:path*", "/invitations/:path*", "/sessions/:path*", "/apikeys/:path*", "/service-accounts/:path*", "/threat-center/:path*", "/intel/:path*", "/iocs/:path*", "/attack/:path*", "/mitre/:path*", "/workbench/:path*", "/timeline/:path*", "/sso/:path*", "/mfa/:path*", "/audit/:path*", "/profile/:path*", "/settings/:path*", "/administration/:path*"],
};
