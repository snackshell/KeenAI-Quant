// keenai_quant/frontend/components/analytics/key-metrics.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const metrics = [
    { title: "Total P/L", value: "+$12,480.50", subtext: "+5.21% since last month", positive: true },
    { title: "Sharpe Ratio", value: "2.18", subtext: "Excellent" },
    { title: "Max Drawdown", value: "-3.15%", subtext: "Low Risk", positive: false },
    { title: "Win Rate", value: "72%", subtext: "108/150 trades" },
];

export function KeyMetrics() {
    return (
        <div className="grid grid-cols-2 gap-6">
            {metrics.map((metric) => (
                <Card key={metric.title} className="bg-background-muted border-border-muted">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-text-secondary">{metric.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className={`text-2xl font-bold ${metric.positive ? 'text-success-primary' : 'text-destructive-primary'}`}>
                            {metric.value}
                        </div>
                        <p className="text-xs text-text-tertiary">{metric.subtext}</p>
                    </CardContent>
                </Card>
            ))}
        </div>
    );
}
