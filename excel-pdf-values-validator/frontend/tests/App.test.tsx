import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import { AppContent } from '../src/App';

// Mock the socket service to avoid connection issues in tests
jest.mock('../src/services/socketService', () => ({
  SocketProvider: ({ children }: { children: React.ReactNode }) => <div data-testid="socket-provider">{children}</div>,
  useSocket: () => ({
    socket: null,
    isConnected: false,
    emit: jest.fn(),
  }),
}));

// Mock the theme
jest.mock('../src/styles/theme', () => ({
  theme: {
    colors: {
      primary: { 400: '#3b82f6', 600: '#2563eb', 900: '#1e3a8a' },
      gray: { 50: '#f9fafb', 200: '#e5e7eb', 900: '#111827', 600: '#4b5563' },
      background: '#f9fafb',
      white: '#ffffff',
      red: { 600: '#dc2626' },
      green: { 600: '#16a34a' },
    },
  },
}));

// Mock GlobalStyles
jest.mock('../src/styles/GlobalStyles', () => ({
  GlobalStyles: () => null,
}));

// Mock all the page components to isolate App testing
jest.mock('../src/pages/Dashboard', () => {
  return function MockDashboard() {
    return <div data-testid="dashboard-page">Dashboard Page</div>;
  };
});

jest.mock('../src/pages/Upload', () => {
  return function MockUpload() {
    return <div data-testid="upload-page">Upload Page</div>;
  };
});

jest.mock('../src/pages/Results', () => {
  return function MockResults() {
    return <div data-testid="results-page">Results Page</div>;
  };
});

jest.mock('../src/pages/SystemStatus', () => {
  return function MockSystemStatus() {
    return <div data-testid="system-status-page">System Status Page</div>;
  };
});

jest.mock('../src/pages/Monitoring', () => {
  return function MockMonitoring() {
    return <div data-testid="monitoring-page">Monitoring Page</div>;
  };
});

// Mock the Layout component
jest.mock('../src/components/Layout/Layout', () => {
  return function MockLayout({ children }: { children: React.ReactNode }) {
    return (
      <div data-testid="layout">
        <nav data-testid="navigation">
          <a href="/">Dashboard</a>
          <a href="/upload">Upload Files</a>
          <a href="/results">Results</a>
          <a href="/system">System Status</a>
          <a href="/monitoring">Monitoring</a>
        </nav>
        <main data-testid="main-content">{children}</main>
      </div>
    );
  };
});

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <AppContent />
      </MemoryRouter>
    );
    
    expect(screen.getByTestId('socket-provider')).toBeInTheDocument();
    expect(screen.getByTestId('layout')).toBeInTheDocument();
  });

  it('renders dashboard page by default', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <AppContent />
      </MemoryRouter>
    );
    
    expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
    expect(screen.getByText('Dashboard Page')).toBeInTheDocument();
  });

  it('renders upload page when navigating to /upload', () => {
    render(
      <MemoryRouter initialEntries={['/upload']}>
        <AppContent />
      </MemoryRouter>
    );
    
    expect(screen.getByTestId('upload-page')).toBeInTheDocument();
    expect(screen.getByText('Upload Page')).toBeInTheDocument();
  });

  it('renders results page when navigating to /results', () => {
    render(
      <MemoryRouter initialEntries={['/results']}>
        <AppContent />
      </MemoryRouter>
    );
    
    expect(screen.getByTestId('results-page')).toBeInTheDocument();
    expect(screen.getByText('Results Page')).toBeInTheDocument();
  });

  it('renders system status page when navigating to /system', () => {
    render(
      <MemoryRouter initialEntries={['/system']}>
        <AppContent />
      </MemoryRouter>
    );
    
    expect(screen.getByTestId('system-status-page')).toBeInTheDocument();
    expect(screen.getByText('System Status Page')).toBeInTheDocument();
  });

  it('renders monitoring page when navigating to /monitoring', () => {
    render(
      <MemoryRouter initialEntries={['/monitoring']}>
        <AppContent />
      </MemoryRouter>
    );
    
    expect(screen.getByTestId('monitoring-page')).toBeInTheDocument();
    expect(screen.getByText('Monitoring Page')).toBeInTheDocument();
  });

  it('provides all necessary context providers', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <AppContent />
      </MemoryRouter>
    );
    
    // QueryClient, Theme, and Socket providers should be available
    expect(screen.getByTestId('socket-provider')).toBeInTheDocument();
    expect(screen.getByTestId('layout')).toBeInTheDocument();
  });

  it('contains navigation links to all main pages', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <AppContent />
      </MemoryRouter>
    );
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Upload Files')).toBeInTheDocument();
    expect(screen.getByText('Results')).toBeInTheDocument();
    expect(screen.getByText('System Status')).toBeInTheDocument();
    expect(screen.getByText('Monitoring')).toBeInTheDocument();
  });
});

