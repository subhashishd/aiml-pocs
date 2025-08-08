import React from 'react';
import styled, { keyframes } from 'styled-components';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
}

const spin = keyframes`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
`;

const getSizeStyles = (size: string) => {
  switch (size) {
    case 'small':
      return {
        width: '16px',
        height: '16px',
        borderWidth: '2px',
      };
    case 'large':
      return {
        width: '32px',
        height: '32px',
        borderWidth: '3px',
      };
    default: // medium
      return {
        width: '24px',
        height: '24px',
        borderWidth: '2px',
      };
  }
};

const SpinnerContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
`;

const Spinner = styled.div<LoadingSpinnerProps>`
  ${({ size = 'medium' }) => {
    const styles = getSizeStyles(size);
    return `
      width: ${styles.width};
      height: ${styles.height};
      border: ${styles.borderWidth} solid transparent;
    `;
  }}
  
  border-top-color: ${({ color, theme }) => color || theme.colors.primary[600]};
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
`;

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  color,
}) => {
  return (
    <SpinnerContainer>
      <Spinner size={size} color={color} />
    </SpinnerContainer>
  );
};
