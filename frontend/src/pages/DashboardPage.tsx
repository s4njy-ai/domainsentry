import { useQuery } from '@tanstack/react-query';
import { 
  Activity, 
  ShieldAlert, 
  Globe,
  BarChart3,
  Clock
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { domainApi, riskApi, feedApi } from '../lib/api';
import { DomainStats, RiskTrend, NewsFeedItem } from '../lib/types';
import { RiskChart } from '../components/charts/RiskChart';
import { TldDistributionChart } from '../components/charts/TldDistributionChart';

export const DashboardPage: React.FC = () => {
  const { data: stats, isLoading: isStatsLoading, isError: isStatsError } = useQuery({
    queryKey: ['domainStats'],
    queryFn: () => domainApi.getDomainStats().then(res => res.data as DomainStats),
  });

  const { data: riskTrends, isLoading: isRiskTrendsLoading } = useQuery({
    queryKey: ['riskTrends'],
    queryFn: () => riskApi.getRiskTrends(30).then(res => {
      // Handle the API response - if it returns an array directly, wrap it in the proper structure
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

  const { data: newsItems, isLoading: isNewsLoading } = useQuery({
    queryKey: ['newsFeeds'],
    queryFn: () => feedApi.getNewsFeeds({ size: 3 }).then(res => res.data.items as NewsFeedItem[]),
  });

  const renderStatCard = (title: string, value: string | number, icon: React.ReactNode, color: string) => (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className={`p-2 rounded-full ${color}`}>
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
      </CardContent>
    </Card>
  );

  if (isStatsError) {
    return (
      <div className="p-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="mt-6 text-red-500">Failed to load dashboard data. Please try again later.</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Overview of domain monitoring and risk analysis</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {isStatsLoading ? (
          <>
            {[1, 2, 3, 4].map(i => (
              <Card key={i}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-8 w-8 rounded-full" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-8 w-16" />
                </CardContent>
              </Card>
            ))}
          </>
        ) : stats ? (
          <>
            {renderStatCard(
              "Total Domains",
              stats.total_domains,
              <Globe className="h-4 w-4 text-blue-500" />,
              "bg-blue-100 text-blue-500"
            )}
            {renderStatCard(
              "Active Domains",
              stats.active_domains,
              <Activity className="h-4 w-4 text-green-500" />,
              "bg-green-100 text-green-500"
            )}
            {renderStatCard(
              "Avg Risk Score",
              `${stats.average_risk_score.toFixed(1)}%`,
              <ShieldAlert className="h-4 w-4 text-orange-500" />,
              "bg-orange-100 text-orange-500"
            )}
            {renderStatCard(
              "Added Today",
              stats.domains_added_today,
              <Clock className="h-4 w-4 text-purple-500" />,
              "bg-purple-100 text-purple-500"
            )}
          </>
        ) : null}
      </div>

      {/* Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Risk Level Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {isStatsLoading ? (
              <Skeleton className="h-64 w-full" />
            ) : stats && stats.risk_distribution ? (
              <div className="space-y-4">
                {Object.entries(stats?.risk_distribution || {}).map(([level, count]) => (
                  <div key={level} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <Badge 
                        variant="outline" 
                        className={
                          level.toLowerCase().includes('high') || level.toLowerCase().includes('critical') 
                            ? 'bg-red-100 text-red-800' 
                            : level.toLowerCase().includes('medium') 
                              ? 'bg-yellow-100 text-yellow-800' 
                              : 'bg-green-100 text-green-800'
                        }
                      >
                        {level}
                      </Badge>
                    </div>
                    <div className="text-right">
                      <span className="font-medium">{count}</span>
                      <span className="text-muted-foreground ml-2">
                        {((count / (stats.total_domains || 1)) * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Average Risk Trend (Last 30 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            {isRiskTrendsLoading ? (
              <Skeleton className="h-64 w-full" />
            ) : riskTrends ? (
              <RiskChart trends={riskTrends || {period_days: 30, trends: [], updated_at: new Date().toISOString()}} />
            ) : null}
          </CardContent>
        </Card>
      </div>

      {/* TLD Distribution and Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>TLD Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            {isStatsLoading ? (
              <Skeleton className="h-64 w-full" />
            ) : stats ? (
              <TldDistributionChart limit={10} />
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {isNewsLoading ? (
                <>
                  {[1, 2, 3].map(i => (
                    <div key={i} className="flex items-start space-x-4">
                      <Skeleton className="h-10 w-10 rounded-full" />
                      <div className="space-y-2 flex-1">
                        <Skeleton className="h-4 w-3/4" />
                        <Skeleton className="h-3 w-1/2" />
                      </div>
                    </div>
                  ))}
                </>
              ) : newsItems && Array.isArray(newsItems) && newsItems.length > 0 ? (
                newsItems.map((item, index) => (
                  <div key={index} className="flex items-start space-x-4">
                    <div className="bg-blue-100 p-2 rounded-full">
                      <BarChart3 className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-medium truncate">{item.title}</p>
                      <p className="text-sm text-muted-foreground">{item.source}</p>
                      <p className="text-xs text-muted-foreground">{new Date(item.published_at).toLocaleDateString()}</p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-muted-foreground text-center py-8">
                  No recent news items available
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Sources and Disclaimer */}
      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="flex flex-wrap justify-center items-center gap-4 mb-3">
          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">crt.sh</span>
          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">RSS Feeds</span>
          <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">WHOIS</span>
          <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">VirusTotal</span>
        </div>
        <p className="text-sm text-blue-800 text-center">
          Non-profit OSINT tool. Data from public sources only. Risk scores for research purposes only.
        </p>
      </div>
    </div>
  );
};