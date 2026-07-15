import { AuthStateShell } from "@/identity/shared/auth-state-shell";

export default function LoadingSessionPage(): React.JSX.Element {
  return <AuthStateShell title="Loading session" description="Restoring your tenant, organization, and workspace context before rendering the protected shell." accent="Session restore" actions={[{ label: "Continue to login", href: "/login", variant: "secondary" }]} />;
}