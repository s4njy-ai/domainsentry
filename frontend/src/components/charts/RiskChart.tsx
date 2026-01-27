import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

import { DailyTimelineItem } from '../../lib/types';

interface RiskChartProps {
  trends: DailyTimelineItem[];
}

export const RiskChart: React.FC<RiskChartProps> = ({ trends }) => {
  // Transform the data to have consistent field names for the chart
  const chartData = trends.map(item => ({
    date: item.date,
    risk: item.avg_risk_score,
    count: item.domain_count
  }));

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={chartData}
          margin={{
            top: 10,
            right: 30,
            left: 0,
            bottom: 0,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => {
              // Format date to show only day/month
              return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }}
          />
          <YAxis 
            yAxisId="left"
            domain={[0, 100]}
            tick={{ fontSize: 12 }}
          />
          <YAxis 
            yAxisId="right" 
            orientation="right" 
            domain={[0, Math.max(...chartData.map(d => d.count)) * 1.2]}
            tick={{ fontSize: 12 }}
          />
          <Tooltip 
            formatter={(value, name) => {
              if (name === 'risk') {
                return [`${Number(value).toFixed(2)}%`, 'Avg Risk Score'];
              }
              return [value, 'Domain Count'];
            }}
            labelFormatter={(label) => `Date: ${new Date(label).toLocaleDateString()}`}
          />
          <Area 
            yAxisId="left"
            type="monotone" 
            dataKey="risk" 
            stroke="#ef4444" 
            fill="#fee2e2" 
            name="Avg Risk Score"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};