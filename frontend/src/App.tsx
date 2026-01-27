import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { ClerkProvider, SignedIn, SignedOut } from '@clerk/clerk-react';

import { ThemeProvider } from './contexts/ThemeContext';
import { Header } from './components/layout/Header';
import { Sidebar } from './components/layout/Sidebar';
import { DashboardPage } from './pages/DashboardPage';
import { DomainsPage } from './pages/DomainsPage';
import { DomainDetailPage } from './pages/DomainDetailPage';
import { RiskAnalysisPage } from './pages/RiskAnalysisPage';
import { NewsFeedsPage } from './pages/NewsFeedsPage';
import { LoginPage } from './pages/LoginPage';
import { ProtectedRoute } from './components/ProtectedRoute';

// Initialize query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
    },
  },
});

// Clerk publishable key from environment
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;

function App() {
  return (
    <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <Router>
            <div className="flex h-screen bg-background">
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route
                  path="/*"
                  element={
                    <SignedIn>
                      <AppLayout />
                    </SignedIn>
                  }
                />
                <Route
                  path="/*"
                  element={
                    <SignedOut>
                      <Navigate to="/login" />
                    </SignedOut>
                  }
                />
              </Routes>
            </div>
          </Router>
          <Toaster position="bottom-right" richColors />
        </ThemeProvider>
      </QueryClientProvider>
    </ClerkProvider>
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
            <Route 
              path="/" 
              element={
                <ProtectedRoute>
                  <DashboardPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/domains" 
              element={
                <ProtectedRoute>
                  <DomainsPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/domains/:id" 
              element={
                <ProtectedRoute>
                  <DomainDetailPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/risk-analysis" 
              element={
                <ProtectedRoute>
                  <RiskAnalysisPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/news-feeds" 
              element={
                <ProtectedRoute>
                  <NewsFeedsPage />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </main>
      </div>
    </>
  );
}

export default App;