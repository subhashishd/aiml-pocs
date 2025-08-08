import React, { createContext, useContext, ReactNode } from 'react';

interface AnalyticsContextType {
  trackEvent: (eventName: string, properties?: Record<string, any>) => void;
  identifyUser: (userId: string, traits?: Record<string, any>) => void;
  trackPageView: (page: string, properties?: Record<string, any>) => void;
}

const AnalyticsContext = createContext<AnalyticsContextType | undefined>(undefined);

interface AnalyticsProviderProps {
  children: ReactNode;
}

export const AnalyticsProvider: React.FC<AnalyticsProviderProps> = ({ children }) => {
  const trackEvent = (eventName: string, properties?: Record<string, any>) => {
    // In development, just log to console
    if (process.env.NODE_ENV === 'development') {
      console.log('Analytics Event:', eventName, properties);
      return;
    }
    
    // In production, you would integrate with your analytics service
    // Examples: Google Analytics, Mixpanel, Segment, etc.
  };

  const identifyUser = (userId: string, traits?: Record<string, any>) => {
    if (process.env.NODE_ENV === 'development') {
      console.log('Analytics Identify:', userId, traits);
      return;
    }
    
    // Production user identification logic
  };

  const trackPageView = (page: string, properties?: Record<string, any>) => {
    if (process.env.NODE_ENV === 'development') {
      console.log('Analytics Page View:', page, properties);
      return;
    }
    
    // Production page view tracking
  };

  const value = {
    trackEvent,
    identifyUser,
    trackPageView,
  };

  return (
    <AnalyticsContext.Provider value={value}>
      {children}
    </AnalyticsContext.Provider>
  );
};

export const useAnalytics = () => {
  const context = useContext(AnalyticsContext);
  if (context === undefined) {
    throw new Error('useAnalytics must be used within an AnalyticsProvider');
  }
  return context;
};
