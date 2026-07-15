import { Card } from "@/components/ui/surfaces";

export default function MaintenancePage(): React.JSX.Element {
  return <Card className="max-w-xl text-center"><h2 className="text-3xl font-semibold">Maintenance mode</h2><p className="mt-3 text-sm text-muted">The platform is temporarily unavailable for maintenance.</p></Card>;
}
