import { AuthStateShell } from "@/identity/shared/auth-state-shell";

export default function DisabledAccountPage(): React.JSX.Element {
  return <AuthStateShell title="Account disabled" description="Your account is currently disabled by an administrator. Re-enable access through the enterprise support process." accent="Administrative status" actions={[{ label: "Return to login", href: "/login", variant: "secondary" }]} />;
}