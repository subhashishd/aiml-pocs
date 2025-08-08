import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import { render, mockApiResponse, mockApiError, createTestQueryClient } from '../test-utils';
import Dashboard from './Dashboard';
import { api } from '../services/apiClient';

// Mock the getStats and getRecent API calls
jest.mock('../services/apiClient');

const mockedApi = api as jest.Mocked<typeof api>;

// Sample test data
const statsMockData = {
  totalTasks: 10,
  completedTasks: 7,
  failedTasks: 1,
  pendingTasks: 2,
};

const recentTasksMockData = [
  { id: '1', filename: 'file1.pdf', status: 'completed', created_at: '2023-01-01T00:00:00Z' },
  { id: '2', filename: 'file2.pdf', status: 'failed', created_at: '2023-01-02T00:00:00Z' },
  { id: '3', filename: 'file3.pdf', status: 'processing', created_at: '2023-01-03T00:00:00Z' },
];

// Test suite for Dashboard
describe('Dashboard Page', () => {

  // Test for successful data fetching
  it('renders the dashboard with data', async () => {
    // Mock the API response
    mockedApi.get.mockResolvedValueOnce(statsMockData);
    mockedApi.get.mockResolvedValueOnce(recentTasksMockData);

    const queryClient = createTestQueryClient();

    // Render the component
    render(<Dashboard />, { queryClient });

    // Wait for element to be in the document
    await waitFor(() => expect(screen.getByText('Welcome to ValidatorAI')).toBeInTheDocument());

    // Check for the rendered elements
    expect(screen.getByText('10')).toBeInTheDocument();
    expect(screen.getByText('Completed')).toBeInTheDocument();
    expect(screen.getByText('file1.pdf')).toBeInTheDocument();
    expect(screen.getByText('file2.pdf')).toBeInTheDocument();
  });

  // Test for error state
  it('handles error state when data fetching fails', async () => {
    // Mock the API error response
    mockedApi.get.mockRejectedValueOnce(mockApiError(500, 'Server error'));
    mockedApi.get.mockRejectedValueOnce(mockApiError(500, 'Server error'));

    const queryClient = createTestQueryClient();

    // Render the component
    render(<Dashboard />, { queryClient });

    // Expect error message to be displayed
    await waitFor(() => {
      expect(screen.getByText('An error occurred')).toBeInTheDocument();
    });
  });

  it('matches snapshot', () => {
    const queryClient = createTestQueryClient();

    // Render the component
    const { asFragment } = render(<Dashboard />, { queryClient });

    // Snapshot match
    expect(asFragment()).toMatchSnapshot();
  });

});
