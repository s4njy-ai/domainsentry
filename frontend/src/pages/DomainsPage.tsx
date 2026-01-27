

import { useQuery } from '@tanstack/react-query';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '../components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { domainApi } from '../lib/api';
import { Domain } from '../lib/types';

export const DomainsPage = () => {
  const { data: domainsData, isLoading, isError } = useQuery({
    queryKey: ['domains'],
    queryFn: () => domainApi.getDomains({ page: 1, size: 20 }).then(res => res.data),
  });

  if (isError) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-foreground">Domains</h1>
        <div className="text-red-500">Failed to load domains. Please try again later.</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-foreground">Domains</h1>
      {isLoading ? (
        <Card>
          <CardHeader>
            <CardTitle>Domains</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Domain</TableHead>
                  <TableHead>Risk Score</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Registrar</TableHead>
                  <TableHead>Updated</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {[...Array(5)].map((_, i) => (
                  <TableRow key={i}>
                    <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                    <TableCell><Skeleton className="h-4 w-20" /></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ) : domainsData?.items && domainsData.items.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Domain List ({domainsData.total})</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Domain</TableHead>
                  <TableHead>Risk Score</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Registrar</TableHead>
                  <TableHead>Updated</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {domainsData.items.map((domain: Domain) => (
                  <TableRow key={domain.id}>
                    <TableCell className="font-medium">
                      <a 
                        href={`/domains/${domain.id}`} 
                        className="hover:underline"
                      >
                        {domain.domain_name}
                      </a>
                    </TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline" 
                        className={
                          domain.risk_score >= 70 
                            ? 'bg-red-100 text-red-800' 
                            : domain.risk_score >= 40 
                              ? 'bg-yellow-100 text-yellow-800' 
                              : 'bg-green-100 text-green-800'
                        }
                      >
                        {domain.risk_score}%
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={domain.is_active ? "default" : "secondary"}>
                        {domain.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </TableCell>
                    <TableCell>{domain.registrar || 'N/A'}</TableCell>
                    <TableCell>{new Date(domain.updated_at).toLocaleDateString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ) : (
        <div className="text-center py-8 text-muted-foreground">
          No domains found.
        </div>
      )}
    </div>
  );
};