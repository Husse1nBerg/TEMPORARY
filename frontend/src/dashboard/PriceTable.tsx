'use client';

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Price } from '@/hooks/usePrices';
import { formatCurrency, timeAgo } from '@/lib/utils';
import StockStatus from './StockStatus';
import PriceTrend from './PriceTrend';

interface PriceTableProps {
  prices: Price[];
  isLoading: boolean;
}

export default function PriceTable({ prices, isLoading }: PriceTableProps) {
  if (isLoading) {
    return <p>Loading price data...</p>;
  }

  if (!prices.length) {
    return <p>No prices found for the selected filters.</p>;
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Product</TableHead>
          <TableHead>Store</TableHead>
          <TableHead>Status</TableHead>
          <TableHead className="text-right">Price</TableHead>
          <TableHead className="text-right">Change (24h)</TableHead>
          <TableHead>Last Updated</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {prices.map((price) => (
          <TableRow key={price.id}>
            <TableCell className="font-medium">{price.product_name}</TableCell>
            <TableCell>{price.store_name}</TableCell>
            <TableCell>
              <StockStatus isAvailable={price.is_available} />
            </TableCell>
            <TableCell className="text-right font-bold">{formatCurrency(price.price)}</TableCell>
            <TableCell className="text-right">
              <PriceTrend changePercent={price.price_change_percent} />
            </TableCell>
            <TableCell>{timeAgo(price.scraped_at)}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}