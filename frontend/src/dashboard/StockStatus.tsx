'use client';

import { Badge } from '@/components/ui/badge';

interface StockStatusProps {
  isAvailable: boolean;
}

export default function StockStatus({ isAvailable }: StockStatusProps) {
  return (
    <Badge variant={isAvailable ? 'default' : 'destructive'}>
      {isAvailable ? 'In Stock' : 'Out of Stock'}
    </Badge>
  );
}