'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowDown, ArrowUp, Minus } from 'lucide-react';

interface PriceCardProps {
  productName: string;
  storeName: string;
  price: number;
  priceChange: number;
  priceChangePercent: number;
  isAvailable: boolean;
}

const PriceCard: React.FC<PriceCardProps> = ({
  productName,
  storeName,
  price,
  priceChange,
  priceChangePercent,
  isAvailable,
}) => {
  const priceChangeIcon =
    priceChange > 0 ? (
      <ArrowUp className="w-4 h-4 text-red-500" />
    ) : priceChange < 0 ? (
      <ArrowDown className="w-4 h-4 text-green-500" />
    ) : (
      <Minus className="w-4 h-4 text-gray-500" />
    );

  return (
    <Card>
      <CardHeader>
        <CardTitle>{productName}</CardTitle>
        <p className="text-sm text-muted-foreground">{storeName}</p>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <p className="text-2xl font-bold">{price.toFixed(2)} EGP</p>
          <div className="flex items-center space-x-2">
            {priceChangeIcon}
            <span
              className={`text-sm font-medium ${
                priceChange > 0 ? 'text-red-500' : priceChange < 0 ? 'text-green-500' : 'text-gray-500'
              }`}
            >
              {priceChangePercent.toFixed(2)}%
            </span>
          </div>
        </div>
        <Badge variant={isAvailable ? 'default' : 'destructive'} className="mt-4">
          {isAvailable ? 'In Stock' : 'Out of Stock'}
        </Badge>
      </CardContent>
    </Card>
  );
};

export default PriceCard;