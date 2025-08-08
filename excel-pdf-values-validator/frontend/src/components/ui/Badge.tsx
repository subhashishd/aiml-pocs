import React from 'react';
import styled, { css, DefaultTheme } from 'styled-components';

interface BadgeProps {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  size?: 'small' | 'medium';
  children: React.ReactNode;
}

const getVariantStyles = (variant: string, theme: DefaultTheme) => {
  switch (variant) {
    case 'success':
      return css`
        background-color: ${theme.colors.green[100]};
        color: ${theme.colors.green[800]};
        border: 1px solid ${theme.colors.green[200]};
      `;
    case 'warning':
      return css`
        background-color: ${theme.colors.yellow[100]};
        color: ${theme.colors.yellow[800]};
        border: 1px solid ${theme.colors.yellow[200]};
      `;
    case 'error':
      return css`
        background-color: ${theme.colors.red[100]};
        color: ${theme.colors.red[800]};
        border: 1px solid ${theme.colors.red[200]};
      `;
    case 'info':
      return css`
        background-color: ${theme.colors.blue[100]};
        color: ${theme.colors.blue[800]};
        border: 1px solid ${theme.colors.blue[200]};
      `;
    default: // default
      return css`
        background-color: ${theme.colors.gray[100]};
        color: ${theme.colors.gray[800]};
        border: 1px solid ${theme.colors.gray[200]};
      `;
  }
};

const getSizeStyles = (size: string) => {
  switch (size) {
    case 'small':
      return css`
        padding: 0.125rem 0.5rem;
        font-size: 0.75rem;
        line-height: 1rem;
      `;
    default: // medium
      return css`
        padding: 0.25rem 0.75rem;
        font-size: 0.875rem;
        line-height: 1.25rem;
      `;
  }
};

const StyledBadge = styled.span<BadgeProps>`
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-weight: 500;
  border-radius: 9999px;
  text-transform: capitalize;
  white-space: nowrap;
  
  ${({ variant = 'default', theme }) => getVariantStyles(variant, theme)}
  ${({ size = 'medium' }) => getSizeStyles(size)}
`;

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'medium',
  ...props
}) => {
  return (
    <StyledBadge variant={variant} size={size} {...props}>
      {children}
    </StyledBadge>
  );
};
