import React from 'react';
import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AnalyticsProvider, useAnalytics } from './AnalyticsProvider';

const TestComponent = () => {
  const { trackEvent } = useAnalytics();

  return (
    <div>
      <button onClick={() => trackEvent('button_click')}>Click Me</button>
    </div>
  );
};

let trackEventMock: jest.Mock;

beforeEach(() => {
  trackEventMock = jest.fn();

  jest.mock('./AnalyticsProvider', () => ({
    useAnalytics: () => ({
      trackEvent: trackEventMock,
    }),
  }));
});

afterEach(() => {
  jest.resetAllMocks();
});

describe('Analytics Provider', () => {
  it('tracks events on button click', async () => {
    const { getByText } = render(
      <AnalyticsProvider>
        <TestComponent />
      </AnalyticsProvider>
    );

    const button = getByText('Click Me');
    await userEvent.click(button);

    expect(trackEventMock).toHaveBeenCalledWith('button_click');
  });
});

