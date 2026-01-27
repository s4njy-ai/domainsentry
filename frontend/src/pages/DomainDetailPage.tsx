

import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Skeleton } from '../components/ui/skeleton';
import { domainApi } from '../lib/api';
import { Domain } from '../lib/types';

export const DomainDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  
  const { data: domain, isLoading, isError } = useQuery({
    queryKey: ['domain', id],
    queryFn: () => domainApi.getDomainById(id!).then(res => res.data as Domain),
    enabled: !!id,
  });

  if (isError) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-foreground">Domain Detail</h1>
        <div className="text-red-500">Failed to load domain data. Please try again later.</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-foreground">
          {isLoading ? <Skeleton className="h-8 w-64" /> : domain?.domain_name}
        </h1>
        {domain && (
          <Badge 
            variant="outline" 
            className={
              domain.risk_score >= 70 
                ? 'border-red-500 bg-red-100 text-red-800' 
                : domain.risk_score >= 40 
                  ? 'border-yellow-500 bg-yellow-100 text-yellow-800' 
                  : 'border-green-500 bg-green-100 text-green-800'
            }
          >
            Risk: {domain.risk_score}%
          </Badge>
        )}
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>WHOIS Data</CardTitle>
            </CardHeader>
            <CardContent>
              <Skeleton className="h-32 w-full" />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Risk Score</CardTitle>
            </CardHeader>
            <CardContent>
              <Skeleton className="h-16 w-32" />
            </CardContent>
          </Card>
        </div>
      ) : domain ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>WHOIS Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Registrar</h4>
                  <p className="text-lg">{domain.registrar || 'N/A'}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Registrant</h4>
                  <p className="text-lg">{domain.registrant_name || 'N/A'}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Organization</h4>
                  <p className="text-lg">{domain.registrant_organization || 'N/A'}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Country</h4>
                  <p className="text-lg">{domain.registrant_country || 'N/A'}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Email</h4>
                  <p className="text-lg">{domain.registrant_email || 'N/A'}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Risk Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="text-center">
                  <div className="text-5xl font-black mb-2">
                    {domain.risk_score}%
                  </div>
                  <Badge 
                    variant="outline" 
                    className={
                      domain.risk_score >= 70 
                        ? 'border-red-500 bg-red-100 text-red-800' 
                        : domain.risk_score >= 40 
                          ? 'border-yellow-500 bg-yellow-100 text-yellow-800' 
                          : 'border-green-500 bg-green-100 text-green-800'
                    }
                  >
                    {domain.risk_score >= 70 ? 'Critical Risk' : 
                     domain.risk_score >= 40 ? 'Medium Risk' : 'Low Risk'}
                  </Badge>
                </div>
                
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground mb-2">Threat Indicators</h4>
                  <div className="flex flex-wrap gap-2">
                    {domain.threat_indicators && domain.threat_indicators.length > 0 ? (
                      domain.threat_indicators.map((indicator, index) => (
                        <Badge key={index} variant="destructive">
                          {indicator}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-muted-foreground">No threat indicators detected</span>
                    )}
                  </div>
                </div>
                
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Name Servers</h4>
                  <ul className="list-disc pl-5 mt-1">
                    {domain.name_servers && domain.name_servers.length > 0 ? (
                      domain.name_servers.map((server, index) => (
                        <li key={index} className="text-sm">{server}</li>
                      ))
                    ) : (
                      <li>N/A</li>
                    )}
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Certificate Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Issuer</h4>
                  <p>{domain.certificate_issuer || 'N/A'}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Subject</h4>
                  <p>{domain.certificate_subject || 'N/A'}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Valid From</h4>
                  <p>{domain.certificate_valid_from ? new Date(domain.certificate_valid_from).toLocaleDateString() : 'N/A'}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Valid To</h4>
                  <p>{domain.certificate_valid_to ? new Date(domain.certificate_valid_to).toLocaleDateString() : 'N/A'}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}
    </div>
  );
};