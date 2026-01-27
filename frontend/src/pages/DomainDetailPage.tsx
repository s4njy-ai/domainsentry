

export const DomainDetailPage = () => (
  <div className="space-y-6">
    <h1 className="text-3xl font-bold text-foreground">Domain Detail</h1>
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="p-6 bg-card rounded-xl shadow-sm">
        <h3 className="text-xl font-semibold mb-4">WHOIS Data</h3>
        <pre className="text-sm bg-muted p-4 rounded-lg overflow-auto">Mock WHOIS...</pre>
      </div>
      <div className="p-6 bg-card rounded-xl shadow-sm">
        <h3 className="text-xl font-semibold mb-4">Risk Score</h3>
        <div className="text-5xl font-black text-destructive">87</div>
        <p className="text-muted-foreground">High Risk</p>
      </div>
    </div>
  </div>
);