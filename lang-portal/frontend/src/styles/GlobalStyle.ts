import { createGlobalStyle } from 'styled-components';
import { theme } from './theme';

export const GlobalStyle = createGlobalStyle`
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: 'Roboto', 'Arial', sans-serif;
    background-color: ${theme.colors.snow2};
    color: ${theme.colors.textDark};
    line-height: 1.6;
  }

  h1, h2, h3, h4, h5, h6 {
    margin-bottom: 0.5rem;
    font-weight: 500;
    line-height: 1.2;
  }

  a {
    color: ${theme.colors.frost3};
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }

  button {
    cursor: pointer;
  }

  /* Make scrollbars more attractive */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  ::-webkit-scrollbar-track {
    background: ${theme.colors.snow1};
  }

  ::-webkit-scrollbar-thumb {
    background: ${theme.colors.frost1};
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: ${theme.colors.frost2};
  }

  /* Utility classes */
  .text-center {
    text-align: center;
  }

  .mb-1 {
    margin-bottom: ${theme.spacing.sm};
  }

  .mb-2 {
    margin-bottom: ${theme.spacing.md};
  }

  .mb-3 {
    margin-bottom: ${theme.spacing.lg};
  }

  .mb-4 {
    margin-bottom: ${theme.spacing.xl};
  }
`;

export default GlobalStyle; 