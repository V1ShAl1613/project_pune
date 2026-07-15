import { AuthStateShell } from "@/identity/shared/auth-state-shell";

export default function MagicLinkPage(): React.JSX.Element {
  return <AuthStateShell title="Check your inbox" description="We sent a passwordless sign-in link to your email address. Use it to continue into the enterprise control plane." accent="Magic link authentication" actions={[{ label: "Back to login", href: "/login", variant: "secondary" }, { label: "Resend link", href: "/forgot-password" }]} />;
}