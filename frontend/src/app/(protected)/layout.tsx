import { MainLayout } from "@/components/layouts/layouts";

export default function ProtectedLayout({ children }: { children: React.ReactNode }): React.JSX.Element {
  return <MainLayout>{children}</MainLayout>;
}
