import { Footer, ResponsiveSidebar, TopNavigation } from "@/components/layouts/navigation";
import { ContentWrapper, PageContainer } from "@/components/layouts/shell";

export function MainLayout({ children }: { children: React.ReactNode }): React.JSX.Element {
  return <div className="min-h-screen bg-canvas text-text"><TopNavigation /><div className="flex min-h-[calc(100vh-73px)]"><ResponsiveSidebar /><main className="flex-1"><PageContainer><ContentWrapper>{children}</ContentWrapper></PageContainer><Footer /></main></div></div>;
}

export function AuthLayout({ children }: { children: React.ReactNode }): React.JSX.Element {
  return <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(15,23,42,0.08),_transparent_30%),linear-gradient(135deg,_#f8fafc,_#eef2ff)] p-4 text-text dark:bg-canvas"><div className="mx-auto flex min-h-screen max-w-6xl items-center justify-center">{children}</div></div>;
}

export function BlankLayout({ children }: { children: React.ReactNode }): React.JSX.Element {
  return <div className="min-h-screen bg-canvas text-text">{children}</div>;
}
