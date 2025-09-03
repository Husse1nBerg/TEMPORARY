'use client';

import StatsCards from '@/dashboard/StatsCards';
import { usePrices } from '@/hooks/usePrices';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { timeAgo, formatCurrency } from '@/lib/utils';
import { ArrowUp, ArrowDown } from 'lucide-react';

export default function DashboardPage() {
  const { prices, loading } = usePrices({ limit: 10 });

  // Dummy data for stats until API endpoints are ready
  const stats = {
    totalProducts: 50,
    totalStores: 10,
    averagePrice: 45.50,
    deals: 12,
  };

  const getPriceChangeColor = (change: number) => {
    if (change > 0) return 'text-red-500';
    if (change < 0) return 'text-green-500';
    return 'text-gray-500';
  };

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <StatsCards {...stats} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Price Updates</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p>Loading prices...</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Product</TableHead>
                    <TableHead>Store</TableHead>
                    <TableHead>Price</TableHead>
                    <TableHead>Change</TableHead>
                    <TableHead>Updated</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {prices.map((price) => (
                    <TableRow key={price.id}>
                      <TableCell>{price.product_name}</TableCell>
                      <TableCell>{price.store_name}</TableCell>
                      <TableCell className="font-medium">{formatCurrency(price.price)}</TableCell>
                      <TableCell className={getPriceChangeColor(price.price_change_percent)}>
                        <span className="flex items-center">
                          {price.price_change_percent > 0 && <ArrowUp className="h-4 w-4 mr-1" />}
                          {price.price_change_percent < 0 && <ArrowDown className="h-4 w-4 mr-1" />}
                          {price.price_change_percent.toFixed(1)}%
                        </span>
                      </TableCell>
                      <TableCell>{timeAgo(price.scraped_at)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Market Insights (Coming Soon)</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500">AI-powered market analysis and trends will be displayed here.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}