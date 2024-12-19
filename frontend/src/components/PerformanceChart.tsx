'use client'

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

interface PerformanceChartProps {
  data: {
    timestamp: string;
    accuracy: number;
    precision: number;
    latency: number;
    contextRetention: number;
  }[];
}

export default function PerformanceChart({ data }: PerformanceChartProps) {
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="timestamp" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="accuracy" stroke="#2563eb" name="Accuracy" />
        <Line type="monotone" dataKey="precision" stroke="#16a34a" name="Precision" />
        <Line type="monotone" dataKey="latency" stroke="#ca8a04" name="Latency" />
        <Line type="monotone" dataKey="contextRetention" stroke="#9333ea" name="Context" />
      </LineChart>
    </ResponsiveContainer>
  )
} 