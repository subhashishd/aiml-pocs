import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ThemeProvider } from 'styled-components';
import '@testing-library/jest-dom';

// Mock theme for testing
export const mockTheme = {
  colors: {
    primary: {
      50: '#eff6ff',
      400: '#3b82f6',
      600: '#2563eb',
      900: '#1e3a8a',
    },
    gray: {
      50: '#f9fafb',
      200: '#e5e7eb',
      300: '#d1d5db',
      400: '#9ca3af',
      600: '#4b5563',
      700: '#374151',
      800: '#1f2937',
      900: '#111827',
    },
    red: {
      50: '#fef2f2',
      300: '#fca5a5',
      600: '#dc2626',
    },
    green: {
      100: '#dcfce7',
      600: '#16a34a',
    },
    background: '#f9fafb',
    white: '#ffffff',
  },
};

// Create a test query client
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
      mutations: {
        retry: false,
      },
    },
  });

// Mock socket provider
const MockSocketProvider = ({ children }: { children: React.ReactNode }) => (
  <div data-testid="socket-provider">{children}</div>
);

interface AllTheProvidersProps {
  children: React.ReactNode;
  initialEntries?: string[];
}

const AllTheProviders = ({ children, initialEntries = ['/'] }: AllTheProvidersProps) => {
  const testQueryClient = createTestQueryClient();
  
  const Router = initialEntries ? MemoryRouter : BrowserRouter;
  const routerProps = initialEntries ? { initialEntries } : {};

  return (
    <QueryClientProvider client={testQueryClient}>
      <ThemeProvider theme={mockTheme}>
        <MockSocketProvider>
          <Router {...routerProps}>
            {children}
          </Router>
        </MockSocketProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  initialEntries?: string[];
}

const customRender = (
  ui: React.ReactElement,
  { initialEntries, ...options }: CustomRenderOptions = {}
) =>
  render(ui, {
    wrapper: ({ children }) => (
      <AllTheProviders initialEntries={initialEntries}>{children}</AllTheProviders>
    ),
    ...options,
  });

// Mock API responses
export const mockApiResponses = {
  uploadSuccess: {
    taskId: 'test-task-123',
    status: 'processing',
    message: 'Files uploaded successfully',
  },
  uploadError: {
    error: 'File upload failed',
    message: 'Invalid file type',
  },
  validationResults: {
    taskId: 'test-task-123',
    status: 'completed',
    results: {
      totalFields: 10,
      passed: 8,
      failed: 2,
      accuracy: 0.8,
    },
  },
};

// Mock file objects for testing
export const mockFiles = {
  validPdf: new File(['pdf content'], 'test.pdf', { type: 'application/pdf' }),
  validExcel: new File(['excel content'], 'test.xlsx', {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  }),
  invalidFile: new File(['text content'], 'test.txt', { type: 'text/plain' }),
  largePdf: new File([new ArrayBuffer(10 * 1024 * 1024)], 'large.pdf', {
    type: 'application/pdf',
  }),
};

// Common test data
export const testData = {
  validationResults: [
    {
      parameter: 'Volume',
      excelValue: 30.8,
      pdfValue: 30.8,
      unit: 'm³',
      match: true,
      similarity: 1.0,
    },
    {
      parameter: 'Mass',
      excelValue: 13791.1,
      pdfValue: 13790.0,
      unit: 'kg',
      match: false,
      similarity: 0.95,
    },
  ],
  systemStatus: {
    api: 'healthy',
    database: 'healthy',
    processing: 'healthy',
    lastUpdated: new Date().toISOString(),
  },
};

// Helper functions for testing
export const waitForLoadingToFinish = () =>
  new Promise((resolve) => setTimeout(resolve, 0));

export const createMockIntersectionObserver = () => {
  const mockIntersectionObserver = jest.fn();
  mockIntersectionObserver.mockReturnValue({
    observe: () => null,
    unobserve: () => null,
    disconnect: () => null,
  });
  window.IntersectionObserver = mockIntersectionObserver;
};

export const createMockResizeObserver = () => {
  const mockResizeObserver = jest.fn();
  mockResizeObserver.mockReturnValue({
    observe: () => null,
    unobserve: () => null,
    disconnect: () => null,
  });
  window.ResizeObserver = mockResizeObserver;
};

// Setup for drag and drop testing
export const createMockDataTransfer = (files: File[]) => ({
  dataTransfer: {
    files,
    items: files.map((file) => ({
      kind: 'file',
      type: file.type,
      getAsFile: () => file,
    })),
    types: ['Files'],
  },
});

// Re-export everything from @testing-library/react
export * from '@testing-library/react';
export { customRender as render };
