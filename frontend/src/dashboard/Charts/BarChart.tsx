'use client';

import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface BarChartProps {
  data: any[];
  xAxisKey: string;
  yAxisKey: string;
  yAxisLabel?: string;
  barColor?: string;
}

export default function BarChart({
  data,
  xAxisKey,
  yAxisKey,
  yAxisLabel = '',
  barColor = '#22c55e',
}: BarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsBarChart data={data} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xAxisKey} />
        <YAxis label={{ value: yAxisLabel, angle: -90, position: 'insideLeft' }} />
        <Tooltip cursor={{ fill: 'rgba(0,0,0,0.1)' }} />
        <Legend />
        <Bar dataKey={yAxisKey} fill={barColor} />
      </RechartsBarChart>
    </ResponsiveContainer>
  );
}