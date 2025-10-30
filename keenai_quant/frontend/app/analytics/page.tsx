// keenai_quant/frontend/app/analytics/page.tsx
import { Button } from "@/components/ui/button";
import { PerformanceOverview } from "@/components/analytics/performance-overview";
import { KeyMetrics } from "@/components/analytics/key-metrics";
import { AssetAllocation } from "@/components/analytics/asset-allocation";
import { OpenPositions } from "@/components/analytics/open-positions";

export default function AnalyticsPage() {
  return (
    <main className="flex-1 p-6 md:p-8 text-text-primary bg-background">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Analytics Dashboard
          </h1>
          <p className="text-text-secondary mt-1">
            Real-time performance and risk metrics.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="outline" className="hidden sm:flex bg-background-muted border-border-muted hover:bg-background-muted/80">
            <CalendarIcon className="w-4 h-4 mr-2" />
            Last 30 Days
          </Button>
          <Button className="bg-success-primary text-background hover:bg-success-primary/90">
            <PlusIcon className="w-4 h-4 mr-2" />
            New Widget
          </Button>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <PerformanceOverview />
        </div>

        <div className="space-y-6">
          <KeyMetrics />
        </div>
      </div>

      <div className="grid gap-6 mt-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <AssetAllocation />
        </div>
        <div className="md:col-span-2 lg:col-span-2">
          <OpenPositions />
        </div>
      </div>
    </main>
  );
}

function PlusIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 12h14" />
      <path d="M12 5v14" />
    </svg>
  );
}

function CalendarIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
      <line x1="16" x2="16" y1="2" y2="6" />
      <line x1="8" x2="8" y1="2" y2="6" />
      <line x1="3" x2="21" y1="10" y2="10" />
    </svg>
  );
}
