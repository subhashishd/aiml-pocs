import React from 'react';
import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AnalyticsProvider, useAnalytics } from './AnalyticsProvider';

// Mock console.log to avoid noise in tests
const originalConsoleLog = console.log;
const originalNodeEnv = process.env.NODE_ENV;

beforeEach(() => {
  console.log = jest.fn();
  // Ensure we're in development mode for the test
  process.env.NODE_ENV = 'development';
});

afterEach(() => {
  console.log = originalConsoleLog;
  process.env.NODE_ENV = originalNodeEnv;
  jest.clearAllMocks();
});

const TestComponent = () => {
  const { trackEvent } = useAnalytics();

  return (
    <div>
      <button onClick={() => trackEvent('button_click')}>Click Me</button>
    </div>
  );
};

describe('Analytics Provider', () => {
  it('tracks events on button click', async () => {
    const { getByText } = render(
      <AnalyticsProvider>
        <TestComponent />
      </AnalyticsProvider>
    );

    const button = getByText('Click Me');
    await userEvent.click(button);

    // In development mode, events should be logged to console
    expect(console.log).toHaveBeenCalledWith('Analytics Event:', 'button_click', undefined);
  });

  it('provides analytics context to children', () => {
    const TestContextComponent = () => {
      const { trackEvent, identifyUser, trackPageView } = useAnalytics();
      return (
        <div>
          <span data-testid="track-event">{typeof trackEvent}</span>
          <span data-testid="identify-user">{typeof identifyUser}</span>
          <span data-testid="track-page-view">{typeof trackPageView}</span>
        </div>
      );
    };

    const { getByTestId } = render(
      <AnalyticsProvider>
        <TestContextComponent />
      </AnalyticsProvider>
    );

    expect(getByTestId('track-event')).toHaveTextContent('function');
    expect(getByTestId('identify-user')).toHaveTextContent('function');
    expect(getByTestId('track-page-view')).toHaveTextContent('function');
  });

  it('throws error when useAnalytics is used outside provider', () => {
    const TestComponentWithoutProvider = () => {
      const { trackEvent } = useAnalytics();
      return <div>Test</div>;
    };

    // Suppress console.error for this test since we expect an error
    const originalError = console.error;
    console.error = jest.fn();

    expect(() => {
      render(<TestComponentWithoutProvider />);
    }).toThrow('useAnalytics must be used within an AnalyticsProvider');

    console.error = originalError;
  });
});

