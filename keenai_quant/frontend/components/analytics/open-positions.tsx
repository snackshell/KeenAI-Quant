// keenai_quant/frontend/components/analytics/open-positions.tsx
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

const positions = [
    { asset: "XAU/USD", type: "LONG", entry: "2350.10", current: "2365.45", pnl: "+$450.75", pnl_positive: true },
    { asset: "EUR/USD", type: "SHORT", entry: "1.0725", current: "1.0740", pnl: "-$150.00", pnl_positive: false },
    { asset: "BTC/USD", type: "LONG", entry: "68,500.00", current: "69,120.30", pnl: "+$620.30", pnl_positive: true },
];

export function OpenPositions() {
  return (
    <Card className="p-6 bg-background-muted border-border-muted">
      <h2 className="text-xl font-semibold text-text-primary">Open Positions</h2>
      <p className="text-sm text-text-secondary mb-4">Live trades currently in market</p>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="text-text-secondary">ASSET</TableHead>
            <TableHead className="text-text-secondary">TYPE</TableHead>
            <TableHead className="text-text-secondary">ENTRY PRICE</TableHead>
            <TableHead className="text-text-secondary">CURRENT PRICE</TableHead>
            <TableHead className="text-text-secondary text-right">UNREALIZED P/L</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {positions.map((pos) => (
            <TableRow key={pos.asset}>
              <TableCell className="font-medium text-text-primary">{pos.asset}</TableCell>
              <TableCell>
                <Badge variant={pos.type === 'LONG' ? 'success' : 'destructive'}>{pos.type}</Badge>
              </TableCell>
              <TableCell className="text-text-primary">{pos.entry}</TableCell>
              <TableCell className="text-text-primary">{pos.current}</TableCell>
              <TableCell className={`text-right font-medium ${pos.pnl_positive ? 'text-success-primary' : 'text-destructive-primary'}`}>
                {pos.pnl}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </Card>
  );
}
