import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import { render, createTestQueryClient } from '../test-utils';
import Dashboard from './Dashboard';
import { api } from '../services/apiClient';

// Mock the getStats and getRecent API calls
jest.mock('../services/apiClient', () => ({
  api: {
    get: jest.fn(),
  },
}));

const mockedApi = api as jest.Mocked<typeof api>;

// Sample test data
const statsMockData = {
  totalTasks: 10,
  completedTasks: 7,
  failedTasks: 1,
  pendingTasks: 2,
};

const recentTasksMockData = [
  { id: '1', filename: 'file1.pdf', status: 'completed', created_at: '2023-01-01T00:00:00Z', file_type: 'pdf' },
  { id: '2', filename: 'file2.pdf', status: 'failed', created_at: '2023-01-02T00:00:00Z', file_type: 'pdf' },
  { id: '3', filename: 'file3.pdf', status: 'processing', created_at: '2023-01-03T00:00:00Z', file_type: 'pdf' },
];

// Test suite for Dashboard
describe('Dashboard Page', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    mockedApi.get.mockClear();
  });

  // Test for successful data fetching
  it('renders the dashboard with data', async () => {
    // Mock the API response
    mockedApi.get
      .mockResolvedValueOnce(statsMockData)
      .mockResolvedValueOnce(recentTasksMockData);

    const queryClient = createTestQueryClient();

    // Render the component
    render(<Dashboard />, { queryClient });

    // Wait for element to be in the document
    await waitFor(() => expect(screen.getByText('Welcome to ValidatorAI')).toBeInTheDocument());

    // Wait for data to load and check for the rendered elements
    await waitFor(() => {
      expect(screen.getByText('10')).toBeInTheDocument();
    }, { timeout: 5000 });
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('file1.pdf')).toBeInTheDocument();
    expect(screen.getByText('file2.pdf')).toBeInTheDocument();
  });

  // Test for loading state
  it('shows loading state initially', () => {
    // Mock API to never resolve (simulate loading)
    mockedApi.get.mockImplementation(() => new Promise(() => {}));
    
    const queryClient = createTestQueryClient();

    // Render the component
    render(<Dashboard />, { queryClient });

    // Should show loading indicators
    expect(screen.getByText('Welcome to ValidatorAI')).toBeInTheDocument();
    expect(screen.getAllByText('--')).toHaveLength(4); // All stat cards show "--" during loading
  });

  // Test for error state - component doesn't show error message, just fails silently
  it('handles error state when data fetching fails', async () => {
    // Mock the API error response with proper error silencing
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    mockedApi.get.mockRejectedValue(new Error('Server error'));

    const queryClient = createTestQueryClient();

    // Render the component
    render(<Dashboard />, { queryClient });

    // Should still show the basic dashboard layout
    expect(screen.getByText('Welcome to ValidatorAI')).toBeInTheDocument();
    expect(screen.getByText('Total Tasks')).toBeInTheDocument();
    
    // Wait for error state to settle
    await waitFor(() => {
      expect(screen.getByText('No tasks yet. Upload your first file to get started!')).toBeInTheDocument();
    }, { timeout: 3000 });
    
    consoleErrorSpy.mockRestore();
  });

  it('matches snapshot', () => {
    const queryClient = createTestQueryClient();

    // Render the component
    const { asFragment } = render(<Dashboard />, { queryClient });

    // Snapshot match
    expect(asFragment()).toMatchSnapshot();
  });

});
