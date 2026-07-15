// Shared icon set for the identity and access management surfaces.
import { Building2, Fingerprint, KeyRound, Landmark, LockKeyhole, ShieldCheck, ShieldUser, Users, Workflow, Globe, MonitorSmartphone, FileClock, BadgeCheck, UserCog, CircleUserRound } from "lucide-react";

export const iamIcons = {
  tenant: ShieldCheck,
  organization: Building2,
  workspace: Landmark,
  user: CircleUserRound,
  role: ShieldUser,
  permission: LockKeyhole,
  group: Users,
  invite: Workflow,
  session: FileClock,
  apiKey: KeyRound,
  serviceAccount: UserCog,
  sso: Globe,
  mfa: Fingerprint,
  device: MonitorSmartphone,
  compliance: BadgeCheck,
};