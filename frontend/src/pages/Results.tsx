import React from 'react';
import styled from 'styled-components';

const ResultsContainer = styled.div`
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

const Results: React.FC = () => {
  return (
    <ResultsContainer>
      <Title>Results</Title>
      <ComingSoon>
        <h2>Results Page Coming Soon</h2>
        <p>This page will show validation results and analytics.</p>
      </ComingSoon>
    </ResultsContainer>
  );
};

export default Results;
