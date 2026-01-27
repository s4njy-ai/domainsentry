

export const RiskAnalysisPage = () => (
  <div className="space-y-6">
    <h1 className="text-3xl font-bold text-foreground">Risk Analysis</h1>
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="p-6 bg-card rounded-xl shadow-sm">
        <h3 className="text-xl font-semibold mb-4">Risk Distribution</h3>
        <div className="w-full h-64 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg animate-pulse flex items-center justify-center text-white font-medium">
          Chart Placeholder
        </div>
      </div>
    </div>
  </div>
);