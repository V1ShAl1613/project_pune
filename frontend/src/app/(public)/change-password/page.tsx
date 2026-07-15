import { AuthStateShell } from "@/identity/shared/auth-state-shell";

export default function ChangePasswordPage(): React.JSX.Element {
  return <AuthStateShell title="Change your password" description="Update your credentials from a secured session or a verified recovery flow." accent="Credential rotation" actions={[{ label: "Sign in", href: "/login", variant: "secondary" }]} />;
}