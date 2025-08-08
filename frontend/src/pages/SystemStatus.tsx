import React from 'react';
import styled from 'styled-components';

const StatusContainer = styled.div`
  padding: 2rem;
`;

const Title = styled.h1`
  margin-bottom: 1.5rem;
  color: #1f2937;
`;

const ComingSoon = styled.div`
  text-align: center;
  padding: 4rem 2rem;
  background: #f9fafb;
  border-radius: 8px;
  border: 2px dashed #d1d5db;
`;

const SystemStatus: React.FC = () => {
  return (
    <StatusContainer>
      <Title>System Status</Title>
      <ComingSoon>
        <h2>System Status Page Coming Soon</h2>
        <p>This page will show system health and status information.</p>
      </ComingSoon>
    </StatusContainer>
  );
};

export default SystemStatus;
