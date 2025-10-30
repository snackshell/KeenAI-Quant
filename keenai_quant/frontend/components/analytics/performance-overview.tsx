// keenai_quant/frontend/components/analytics/performance-overview.tsx
"use client";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Card } from '@/components/ui/card';

const data = [
  { name: 'Jan', 'Strategy A': 4000, 'S&P 500': 2400 },
  { name: 'Feb', 'Strategy A': 3000, 'S&P 500': 1398 },
  { name: 'Mar', 'Strategy A': 2000, 'S&P 500': 9800 },
  { name: 'Apr', 'Strategy A': 2780, 'S&P 500': 3908 },
  { name: 'May', 'Strategy A': 1890, 'S&P 500': 4800 },
  { name: 'Jun', 'Strategy A': 2390, 'S&P 500': 3800 },
  { name: 'Jul', 'Strategy A': 3490, 'S&P 500': 4300 },
];

export function PerformanceOverview() {
  return (
    <Card className="p-6 bg-background-muted border-border-muted">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-xl font-semibold text-text-primary">Performance Overview</h2>
          <p className="text-sm text-text-secondary">Portfolio Value (USD)</p>
        </div>
        <div className="flex items-center space-x-4">
            <div className="flex items-center">
                <span className="w-3 h-3 mr-2 rounded-full bg-success-primary"></span>
                <span className="text-sm text-text-secondary">Strategy A</span>
            </div>
            <div className="flex items-center">
                <span className="w-3 h-3 mr-2 rounded-full bg-info-primary"></span>
                <span className="text-sm text-text-secondary">S&P 500</span>
            </div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorStrategyA" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--color-success-primary)" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="var(--color-success-primary)" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorSP500" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--color-info-primary)" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="var(--color-info-primary)" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <XAxis dataKey="name" stroke="var(--color-border-muted)" />
          <YAxis stroke="var(--color-border-muted)" />
          <Tooltip contentStyle={{ backgroundColor: 'var(--color-background-muted)', border: '1px solid var(--color-border-muted)' }} />
          <Area type="monotone" dataKey="Strategy A" stroke="var(--color-success-primary)" fillOpacity={1} fill="url(#colorStrategyA)" />
          <Area type="monotone" dataKey="S&P 500" stroke="var(--color-info-primary)" fillOpacity={1} fill="url(#colorSP500)" />
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  );
}
