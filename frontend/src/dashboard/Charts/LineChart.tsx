'use client';

import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface LineChartProps {
  data: any[]; // Expects an array of data objects
  xAxisKey: string; // Key for the x-axis (e.g., "date")
  yAxisKey: string; // Key for the y-axis (e.g., "price")
  yAxisLabel?: string;
  lineColor?: string;
}

export default function LineChart({
  data,
  xAxisKey,
  yAxisKey,
  yAxisLabel = '',
  lineColor = '#16a34a',
}: LineChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsLineChart data={data} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey={xAxisKey} />
        <YAxis label={{ value: yAxisLabel, angle: -90, position: 'insideLeft' }} />
        <Tooltip
          formatter={(value: number) =>
            typeof value === 'number' ? `EGP ${value.toFixed(2)}` : value
          }
        />
        <Legend />
        <Line type="monotone" dataKey={yAxisKey} stroke={lineColor} activeDot={{ r: 8 }} />
      </RechartsLineChart>
    </ResponsiveContainer>
  );
}