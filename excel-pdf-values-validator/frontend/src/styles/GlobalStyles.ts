import { createGlobalStyle } from 'styled-components';

export const GlobalStyles = createGlobalStyle`
  /* CSS Reset and Base Styles */
  *,
  *::before,
  *::after {
    box-sizing: border-box;
  }

  html {
    line-height: 1.15;
    -webkit-text-size-adjust: 100%;
  }

  body {
    margin: 0;
    font-family: ${({ theme }) => theme.fonts.sans};
    font-size: ${({ theme }) => theme.fontSizes.base};
    line-height: ${({ theme }) => theme.lineHeights.normal};
    color: ${({ theme }) => theme.colors.gray[900]};
    background-color: ${({ theme }) => theme.colors.background};
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  /* Reset margins and paddings */
  h1, h2, h3, h4, h5, h6, p, ul, ol, li, figure, figcaption, blockquote, dl, dd {
    margin: 0;
    padding: 0;
  }

  /* Headings */
  h1, h2, h3, h4, h5, h6 {
    font-weight: ${({ theme }) => theme.fontWeights.semibold};
    line-height: ${({ theme }) => theme.lineHeights.tight};
  }

  h1 {
    font-size: ${({ theme }) => theme.fontSizes['3xl']};
  }

  h2 {
    font-size: ${({ theme }) => theme.fontSizes['2xl']};
  }

  h3 {
    font-size: ${({ theme }) => theme.fontSizes.xl};
  }

  h4 {
    font-size: ${({ theme }) => theme.fontSizes.lg};
  }

  h5 {
    font-size: ${({ theme }) => theme.fontSizes.base};
  }

  h6 {
    font-size: ${({ theme }) => theme.fontSizes.sm};
  }

  /* Links */
  a {
    color: ${({ theme }) => theme.colors.primary[600]};
    text-decoration: none;
    transition: color ${({ theme }) => theme.transitions.fast};
  }

  a:hover {
    color: ${({ theme }) => theme.colors.primary[700]};
  }

  a:focus {
    outline: 2px solid ${({ theme }) => theme.colors.primary[500]};
    outline-offset: 2px;
  }

  /* Buttons */
  button {
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
    margin: 0;
  }

  button:focus {
    outline: none;
  }

  /* Form elements */
  input,
  textarea,
  select {
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
    margin: 0;
  }

  input[type="text"],
  input[type="email"],
  input[type="password"],
  input[type="number"],
  input[type="search"],
  input[type="url"],
  textarea,
  select {
    appearance: none;
    background-color: ${({ theme }) => theme.colors.white};
    border: 1px solid ${({ theme }) => theme.colors.gray[300]};
    border-radius: ${({ theme }) => theme.radii.md};
    padding: 0.5rem 0.75rem;
    transition: border-color ${({ theme }) => theme.transitions.fast},
                box-shadow ${({ theme }) => theme.transitions.fast};
  }

  input[type="text"]:focus,
  input[type="email"]:focus,
  input[type="password"]:focus,
  input[type="number"]:focus,
  input[type="search"]:focus,
  input[type="url"]:focus,
  textarea:focus,
  select:focus {
    outline: none;
    border-color: ${({ theme }) => theme.colors.primary[500]};
    box-shadow: 0 0 0 3px ${({ theme }) => theme.colors.primary[100]};
  }

  /* Lists */
  ul, ol {
    list-style: none;
  }

  /* Images */
  img {
    max-width: 100%;
    height: auto;
  }

  /* Tables */
  table {
    border-collapse: collapse;
    border-spacing: 0;
    width: 100%;
  }

  th,
  td {
    text-align: left;
    padding: 0.75rem;
    border-bottom: 1px solid ${({ theme }) => theme.colors.gray[200]};
  }

  th {
    font-weight: ${({ theme }) => theme.fontWeights.semibold};
    color: ${({ theme }) => theme.colors.gray[700]};
    background-color: ${({ theme }) => theme.colors.gray[50]};
  }

  /* Code */
  code,
  pre {
    font-family: ${({ theme }) => theme.fonts.mono};
    font-size: 0.875em;
  }

  code {
    background-color: ${({ theme }) => theme.colors.gray[100]};
    padding: 0.125rem 0.25rem;
    border-radius: ${({ theme }) => theme.radii.sm};
  }

  pre {
    background-color: ${({ theme }) => theme.colors.gray[100]};
    padding: 1rem;
    border-radius: ${({ theme }) => theme.radii.md};
    overflow-x: auto;
  }

  pre code {
    background-color: transparent;
    padding: 0;
  }

  /* Scrollbars */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  ::-webkit-scrollbar-track {
    background: ${({ theme }) => theme.colors.gray[100]};
  }

  ::-webkit-scrollbar-thumb {
    background: ${({ theme }) => theme.colors.gray[400]};
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: ${({ theme }) => theme.colors.gray[500]};
  }

  /* Selection */
  ::selection {
    background-color: ${({ theme }) => theme.colors.primary[100]};
    color: ${({ theme }) => theme.colors.primary[900]};
  }

  /* Focus visible for accessibility */
  .js-focus-visible :focus:not(.focus-visible) {
    outline: none;
  }

  /* Utility classes */
  .sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
  }

  .container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
  }

  /* Responsive utilities */
  @media (min-width: ${({ theme }) => theme.breakpoints.sm}) {
    .container {
      padding: 0 1.5rem;
    }
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.md}) {
    .container {
      padding: 0 2rem;
    }
  }

  /* Print styles */
  @media print {
    *,
    *::before,
    *::after {
      background: transparent !important;
      color: black !important;
      box-shadow: none !important;
      text-shadow: none !important;
    }

    a,
    a:visited {
      text-decoration: underline;
    }

    abbr[title]::after {
      content: " (" attr(title) ")";
    }

    pre,
    blockquote {
      border: 1px solid #999;
      page-break-inside: avoid;
    }

    thead {
      display: table-header-group;
    }

    tr,
    img {
      page-break-inside: avoid;
    }

    p,
    h2,
    h3 {
      orphans: 3;
      widows: 3;
    }

    h2,
    h3 {
      page-break-after: avoid;
    }
  }
`;
