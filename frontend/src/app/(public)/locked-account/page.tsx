import { AuthStateShell } from "@/identity/shared/auth-state-shell";

export default function LockedAccountPage(): React.JSX.Element {
  return <AuthStateShell title="Account locked" description="This account is temporarily locked due to policy or failed sign-in activity. Contact an administrator to restore access." accent="Account protection" actions={[{ label: "Return to login", href: "/login", variant: "secondary" }, { label: "Access denied", href: "/access-denied" }]} />;
}