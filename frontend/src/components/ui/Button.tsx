import React from 'react';
import styled, { css, DefaultTheme } from 'styled-components';

interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'small' | 'medium' | 'large';
  fullWidth?: boolean;
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  as?: React.ElementType;
  to?: string;
}

const getVariantStyles = (variant: string, theme: DefaultTheme) => {
  switch (variant) {
    case 'primary':
      return css`
        background-color: ${theme.colors.primary[600]};
        color: ${theme.colors.white};
        border: 1px solid ${theme.colors.primary[600]};

        &:hover:not(:disabled) {
          background-color: ${theme.colors.primary[700]};
          border-color: ${theme.colors.primary[700]};
        }

        &:focus {
          box-shadow: 0 0 0 3px ${theme.colors.primary[100]};
        }
      `;
    case 'secondary':
      return css`
        background-color: ${theme.colors.gray[100]};
        color: ${theme.colors.gray[900]};
        border: 1px solid ${theme.colors.gray[300]};

        &:hover:not(:disabled) {
          background-color: ${theme.colors.gray[200]};
        }

        &:focus {
          box-shadow: 0 0 0 3px ${theme.colors.gray[100]};
        }
      `;
    case 'outline':
      return css`
        background-color: transparent;
        color: ${theme.colors.primary[600]};
        border: 1px solid ${theme.colors.primary[600]};

        &:hover:not(:disabled) {
          background-color: ${theme.colors.primary[50]};
        }

        &:focus {
          box-shadow: 0 0 0 3px ${theme.colors.primary[100]};
        }
      `;
    case 'ghost':
      return css`
        background-color: transparent;
        color: ${theme.colors.gray[600]};
        border: 1px solid transparent;

        &:hover:not(:disabled) {
          background-color: ${theme.colors.gray[100]};
          color: ${theme.colors.gray[900]};
        }

        &:focus {
          box-shadow: 0 0 0 3px ${theme.colors.gray[100]};
        }
      `;
    case 'danger':
      return css`
        background-color: ${theme.colors.red[600]};
        color: ${theme.colors.white};
        border: 1px solid ${theme.colors.red[600]};

        &:hover:not(:disabled) {
          background-color: ${theme.colors.red[700]};
          border-color: ${theme.colors.red[700]};
        }

        &:focus {
          box-shadow: 0 0 0 3px ${theme.colors.red[100]};
        }
      `;
    default:
      return css``;
  }
};

const getSizeStyles = (size: string) => {
  switch (size) {
    case 'small':
      return css`
        padding: 0.5rem 0.75rem;
        font-size: 0.875rem;
        line-height: 1.25rem;
      `;
    case 'large':
      return css`
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        line-height: 1.5rem;
      `;
    default: // medium
      return css`
        padding: 0.625rem 1rem;
        font-size: 0.875rem;
        line-height: 1.25rem;
      `;
  }
};

const StyledButton = styled.button<ButtonProps>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s ease;
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
  
  ${({ variant = 'primary', theme }) => getVariantStyles(variant, theme)}
  ${({ size = 'medium' }) => getSizeStyles(size)}
  
  ${({ fullWidth }) =>
    fullWidth &&
    css`
      width: 100%;
    `}

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &:focus {
    outline: none;
  }

  ${({ loading }) =>
    loading &&
    css`
      position: relative;
      color: transparent;

      &::after {
        content: '';
        position: absolute;
        width: 16px;
        height: 16px;
        border: 2px solid transparent;
        border-top: 2px solid currentColor;
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }

      @keyframes spin {
        from {
          transform: rotate(0deg);
        }
        to {
          transform: rotate(360deg);
        }
      }
    `}
`;

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'medium',
  fullWidth = false,
  disabled = false,
  loading = false,
  onClick,
  type = 'button',
  as,
  to,
  ...props
}) => {
  return (
    <StyledButton
      variant={variant}
      size={size}
      fullWidth={fullWidth}
      disabled={disabled || loading}
      loading={loading}
      onClick={onClick}
      type={type}
      as={as}
      to={to}
      {...props}
    >
      {children}
    </StyledButton>
  );
};
