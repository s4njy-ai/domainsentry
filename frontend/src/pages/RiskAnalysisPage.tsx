

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { riskApi } from '../lib/api';
import { RiskTrend, FactorBreakdown } from '../lib/types';
import { RiskChart } from '../components/charts/RiskChart';

export const RiskAnalysisPage = () => {
  const { data: riskTrends, isLoading: isRiskTrendsLoading, isError: isRiskTrendsError } = useQuery({
    queryKey: ['riskTrends'],
    queryFn: () => riskApi.getRiskTrends(30).then(res => {
      const rawData = res.data;
      if (Array.isArray(rawData)) {
        return {
          period_days: 30,
          trends: rawData as Array<{date: string; avg_risk_score: number; domain_count: number}>,
          updated_at: new Date().toISOString()
        };
      }
      return rawData as RiskTrend;
    }),
  });

  const { data: factorBreakdown, isLoading: isFactorLoading, isError: isFactorError } = useQuery({
    queryKey: ['factorBreakdown'],
    queryFn: () => riskApi.getFactorBreakdown(30).then(res => res.data as FactorBreakdown),
  });

  if (isRiskTrendsError || isFactorError) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-foreground">Risk Analysis</h1>
        <div className="text-red-500">Failed to load risk analysis data. Please try again later.</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-foreground">Risk Analysis</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Average Risk Trend (Last 30 Days)</CardTitle>
        </CardHeader>
        <CardContent>
          {isRiskTrendsLoading ? (
            <Skeleton className="h-80 w-full" />
          ) : riskTrends ? (
            <RiskChart trends={riskTrends} />
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              No risk trend data available
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Risk Factor Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          {isFactorLoading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map(i => (
                <div key={i} className="flex items-center justify-between">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-4 w-16" />
                </div>
              ))}
            </div>
          ) : factorBreakdown && factorBreakdown.breakdown ? (
            <div className="space-y-4">
              {Object.entries(factorBreakdown.breakdown)
                .sort(([, a], [, b]) => b - a) // Sort by value descending
                .map(([factor, score], index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <Badge 
                        variant="outline" 
                        className="mr-2 capitalize"
                      >
                        {factor.replace(/_/g, ' ')}
                      </Badge>
                    </div>
                    <div className="text-right">
                      <span className="font-medium">{score}%</span>
                    </div>
                  </div>
                ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              No risk factor data available
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};