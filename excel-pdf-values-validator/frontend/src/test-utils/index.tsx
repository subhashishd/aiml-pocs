import React, { ReactElement } from 'react';
import { render, RenderOptions, RenderResult } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from 'styled-components';

import { theme } from '../styles/theme';

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

// Mock socket provider for tests
const MockSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return <div data-testid="mock-socket-provider">{children}</div>;
};

interface AllTheProvidersProps {
  children: React.ReactNode;
  queryClient?: QueryClient;
  initialEntries?: string[];
}

const AllTheProviders: React.FC<AllTheProvidersProps> = ({
  children,
  queryClient = createTestQueryClient(),
  initialEntries = ['/'],
}) => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <MockSocketProvider>
          <BrowserRouter>
            {children}
          </BrowserRouter>
        </MockSocketProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  queryClient?: QueryClient;
  initialEntries?: string[];
}

const customRender = (
  ui: ReactElement,
  options: CustomRenderOptions = {}
): RenderResult => {
  const { queryClient, initialEntries, ...renderOptions } = options;

  return render(ui, {
    wrapper: ({ children }) => (
      <AllTheProviders queryClient={queryClient} initialEntries={initialEntries}>
        {children}
      </AllTheProviders>
    ),
    ...renderOptions,
  });
};

// Mock data factories
export const mockTask = {
  id: 'task-123',
  filename: 'test-file.pdf',
  status: 'completed' as const,
  created_at: '2023-01-01T00:00:00Z',
  file_type: 'pdf' as const,
};

export const mockDashboardStats = {
  totalTasks: 10,
  completedTasks: 7,
  failedTasks: 1,
  pendingTasks: 2,
};

export const mockApiResponse = <T,>(data: T, delay = 0) => {
  return new Promise<T>(resolve => {
    setTimeout(() => resolve(data), delay);
  });
};

export const mockApiError = (status = 500, message = 'Server Error') => {
  return Promise.reject({
    status,
    message,
    data: null,
  });
};

// Mock fetch responses
export const mockFetch = (data: any, ok = true, status = 200) => {
  return jest.fn().mockResolvedValue({
    ok,
    status,
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
  });
};

// Mock file for upload tests
export const createMockFile = (
  name = 'test-file.pdf',
  size = 1024,
  type = 'application/pdf'
) => {
  const file = new File(['mock file content'], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
};

// Wait for async operations
export const waitForLoadingToFinish = async () => {
  const { waitForElementToBeRemoved } = await import('@testing-library/react');
  try {
    await waitForElementToBeRemoved(() => document.querySelector('[data-testid="loading"]'), {
      timeout: 3000,
    });
  } catch (error) {
    // Loading element might not exist
  }
};

// User event utilities
export const setupUser = () => {
  // Dynamic import to avoid issues with Jest hoisting
  const userEvent = require('@testing-library/user-event');
  return userEvent.setup();
};

// Re-export everything
export * from '@testing-library/react';
export { customRender as render };
export { createTestQueryClient };
