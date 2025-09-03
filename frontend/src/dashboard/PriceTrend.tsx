'use client';

import { ArrowUp, ArrowDown, Minus } from 'lucide-react';

interface PriceTrendProps {
  changePercent: number;
}

export default function PriceTrend({ changePercent }: PriceTrendProps) {
  const isUp = changePercent > 0;
  const isDown = changePercent < 0;

  const getColor = () => {
    if (isUp) return 'text-red-500';
    if (isDown) return 'text-green-500';
    return 'text-gray-500';
  };

  const getIcon = () => {
    if (isUp) return <ArrowUp className="h-4 w-4 mr-1" />;
    if (isDown) return <ArrowDown className="h-4 w-4 mr-1" />;
    return <Minus className="h-4 w-4 mr-1" />;
  };

  return (
    <div className={`flex items-center justify-end ${getColor()}`}>
      {getIcon()}
      <span>{Math.abs(changePercent).toFixed(1)}%</span>
    </div>
  );
}