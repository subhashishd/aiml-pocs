import React from 'react';
import styled from 'styled-components';

const MonitoringContainer = styled.div`
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

const Monitoring: React.FC = () => {
  return (
    <MonitoringContainer>
      <Title>Monitoring</Title>
      <ComingSoon>
        <h2>Monitoring Page Coming Soon</h2>
        <p>This page will show system monitoring and analytics.</p>
      </ComingSoon>
    </MonitoringContainer>
  );
};

export default Monitoring;
