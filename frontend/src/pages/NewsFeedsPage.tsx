

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Skeleton } from '../components/ui/skeleton';
import { feedApi } from '../lib/api';
import { NewsFeedItem } from '../lib/types';

export const NewsFeedsPage = () => {
  const { data: newsData, isLoading, isError } = useQuery({
    queryKey: ['newsFeeds'],
    queryFn: () => feedApi.getNewsFeeds({ page: 1, size: 20 }).then(res => res.data),
  });

  if (isError) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-foreground">News Feeds</h1>
        <div className="text-red-500">Failed to load news feeds. Please try again later.</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">News Feeds</h1>
        <div className="flex flex-wrap gap-2 mt-2">
          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">RSS Feeds</span>
          <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Security News</span>
        </div>
      </div>
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <Card key={i}>
              <CardHeader>
                <CardTitle><Skeleton className="h-5 w-3/4" /></CardTitle>
                <CardDescription><Skeleton className="h-4 w-1/2" /></CardDescription>
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6 mt-2" />
              </CardContent>
            </Card>
          ))}
        </div>
      ) : newsData?.items && newsData.items.length > 0 ? (
        <div className="space-y-4">
          {newsData.items.map((item: NewsFeedItem, index: number) => (
            <Card key={index}>
              <CardHeader>
                <CardTitle className="text-lg">
                  <a 
                    href={item.link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="hover:underline"
                  >
                    {item.title}
                  </a>
                </CardTitle>
                <CardDescription>
                  Source: {item.source} • {new Date(item.published_at).toLocaleDateString()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{item.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-muted-foreground">
          No news feeds available at the moment.
        </div>
      )}
    </div>
  );
};