import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from 'styled-components';

// Components
import Layout from './components/Layout/Layout';

// Pages
import Dashboard from './pages/Dashboard';
import Monitoring from './pages/Monitoring';
import Results from './pages/Results';
import SystemStatus from './pages/SystemStatus';
import Upload from './pages/Upload';

// Services
import { SocketProvider } from './services/socketService';

// Styles
import { GlobalStyles } from './styles/GlobalStyles';
import { theme } from './styles/theme';

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

// Separate component for the app content (without Router for testing)
export function AppContent() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <SocketProvider>
          <GlobalStyles />
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/results/:taskId?" element={<Results />} />
              <Route path="/system" element={<SystemStatus />} />
              <Route path="/monitoring" element={<Monitoring />} />
            </Routes>
          </Layout>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1f2937',
                color: '#f9fafb',
                border: '1px solid #374151',
              },
              success: {
                iconTheme: {
                  primary: '#10b981',
                  secondary: '#f9fafb',
                },
              },
              error: {
                iconTheme: {
                  primary: '#ef4444',
                  secondary: '#f9fafb',
                },
              },
            }}
          />
        </SocketProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
