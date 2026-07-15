import { AuthLayout } from "@/components/layouts/layouts";

export default function PublicLayout({ children }: { children: React.ReactNode }): React.JSX.Element {
  return <AuthLayout>{children}</AuthLayout>;
}
