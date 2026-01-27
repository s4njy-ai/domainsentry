import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';

import { ThemeProvider } from './contexts/ThemeContext';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { Footer } from './components/layout/Footer';
import { DashboardPage } from './pages/DashboardPage';
import { DomainsPage } from './pages/DomainsPage';
import { DomainDetailPage } from './pages/DomainDetailPage';
import { RiskAnalysisPage } from './pages/RiskAnalysisPage';
import { NewsFeedsPage } from './pages/NewsFeedsPage';

// Initialize query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <Router>
          <div className="flex flex-col min-h-screen bg-background">
            <div className="flex flex-1 overflow-hidden">
              <AppLayout />
            </div>
            <Footer />
          </div>
        </Router>
        <Toaster position="bottom-right" richColors />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

function AppLayout() {
  return (
    <>
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 bg-muted/40">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/domains" element={<DomainsPage />} />
            <Route path="/domains/:id" element={<DomainDetailPage />} />
            <Route path="/risk-analysis" element={<RiskAnalysisPage />} />
            <Route path="/news-feeds" element={<NewsFeedsPage />} />
          </Routes>
        </main>
      </div>
    </>
  );
}

export default App;