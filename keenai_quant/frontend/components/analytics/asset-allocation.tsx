// keenai_quant/frontend/components/analytics/asset-allocation.tsx
"use client";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';
import { Card } from '@/components/ui/card';

const data = [
  { name: 'Forex (FX)', value: 50 },
  { name: 'Crypto (BTC, ETH)', value: 30 },
  { name: 'Commodities (XAU)', value: 20 },
];

const COLORS = ['#FFBB28', '#00C49F', '#0088FE'];

export function AssetAllocation() {
  return (
    <Card className="p-6 bg-background-muted border-border-muted">
      <h2 className="text-xl font-semibold text-text-primary">Asset Allocation</h2>
      <p className="text-sm text-text-secondary mb-4">Current portfolio distribution</p>
      <div className="grid grid-cols-2">
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
             <Legend layout="vertical" verticalAlign="middle" align="right" />
          </PieChart>
        </ResponsiveContainer>
        <div className="flex flex-col items-center justify-center">
            <span className="text-4xl font-bold text-text-primary">5</span>
            <span className="text-sm text-text-secondary">Assets</span>
        </div>
      </div>
    </Card>
  );
}
