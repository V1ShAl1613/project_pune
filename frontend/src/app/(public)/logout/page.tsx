import { AuthStateShell } from "@/identity/shared/auth-state-shell";

export default function LogoutPage(): React.JSX.Element {
  return <AuthStateShell title="Signed out" description="Your session has been ended locally. Sign in again to continue into the enterprise control plane." accent="Logout complete" actions={[{ label: "Sign in again", href: "/login" }, { label: "Return home", href: "/" , variant: "secondary" }]} />;
}