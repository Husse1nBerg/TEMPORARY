'use client';

import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';
import { usePrices } from '@/hooks/usePrices';

export default function RefreshButton() {
  const { refreshPrices, refreshing } = usePrices();

  return (
    <Button onClick={refreshPrices} disabled={refreshing}>
      <RefreshCw className={`mr-2 h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
      {refreshing ? 'Refreshing...' : 'Refresh Prices'}
    </Button>
  );
}