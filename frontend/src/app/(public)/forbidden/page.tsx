import { AuthStateShell } from "@/identity/shared/auth-state-shell";

export default function ForbiddenPage(): React.JSX.Element {
  return <AuthStateShell title="Forbidden" description="You are authenticated, but this resource is not available for your current role or scope." accent="Authorization state" actions={[{ label: "Open dashboard", href: "/dashboard", variant: "secondary" }, { label: "Access denied", href: "/access-denied" }]} />;
}