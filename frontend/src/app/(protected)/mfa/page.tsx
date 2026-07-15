import { IdentityPageShell } from "@/identity/shared/iam-page-shell";
import { SectionCard, SectionGrid } from "@/identity/shared/iam-section";
import { Badge } from "@/components/ui/surfaces";

export default function MfaPage(): React.JSX.Element {
  return <IdentityPageShell eyebrow="Multi-factor authentication" title="MFA" description="Authenticator app, SMS, email OTP, security keys, passkeys, backup codes, and recovery flows." status="phishing-resistant ready" stats={[{ label: "Methods", value: "6", detail: "UI methods prepared" }, { label: "Recovery", value: "Ready", detail: "Codes and reset UX" }]}>
    <SectionGrid>
      <SectionCard title="Supported factors" description="Frontend surfaces for modern and fallback factors.">
        <div className="flex flex-wrap gap-2"><Badge tone="success">Authenticator app</Badge><Badge tone="success">SMS</Badge><Badge tone="success">Email OTP</Badge><Badge tone="neutral">Security keys</Badge><Badge tone="neutral">Passkeys</Badge><Badge tone="warning">Recovery codes</Badge></div>
      </SectionCard>
      <SectionCard title="Security states" description="Reset and disable flows for admin and self-service operations.">
        <div className="space-y-2 text-sm text-muted"><div>Disable MFA for support workflows.</div><div>Reset MFA after device loss or compromise.</div><div>Show trusted-device enrollment status.</div></div>
      </SectionCard>
    </SectionGrid>
  </IdentityPageShell>;
}