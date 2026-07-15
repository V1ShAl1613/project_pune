import { Spinner } from "@/components/ui/surfaces";

export default function Loading(): React.JSX.Element {
  return <div className="flex min-h-screen items-center justify-center"><Spinner label="Loading application" /></div>;
}
