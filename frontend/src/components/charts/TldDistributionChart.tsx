import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { useQuery } from '@tanstack/react-query';

import { domainApi } from '../../lib/api';
import { TldDistribution } from '../../lib/types';

interface TldDistributionChartProps {
  limit?: number;
}

// Color palette for the pie chart
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A'];

export const TldDistributionChart: React.FC<TldDistributionChartProps> = ({ limit = 10 }) => {
  const [chartData, setChartData] = useState<{ name: string; value: number; count: number }[]>([]);
  
  const { data: rawData, isLoading } = useQuery({
    queryKey: ['tldDistribution', limit],
    queryFn: () => domainApi.getTldDistribution(limit).then(res => res.data as TldDistribution[]),
  });

  useEffect(() => {
    if (rawData && Array.isArray(rawData)) {
      // Transform the data for the chart
      const transformedData = rawData.map((item, index) => ({
        name: item.tld || 'Unknown',
        value: item.count,
        count: item.count,
        // Use index to cycle through colors if we have more items than colors
        color: COLORS[index % COLORS.length]
      }));
      
      setChartData(transformedData);
    } else {
      setChartData([]); // Ensure chartData is an empty array if rawData is not valid
    }
  }, [rawData]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            nameKey="name"
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          >
            {chartData.map((_, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip 
            formatter={(value) => [`${value} domains`, 'Count']}
            labelFormatter={(value) => `TLD: ${value}`}
          />
          <Legend 
            layout="vertical" 
            verticalAlign="middle" 
            align="right"
            formatter={(value, _, index) => {
              const count = chartData[index]?.count || 0;
              return `${value} (${count})`;
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};