import React from 'react';
import styled, { keyframes } from 'styled-components';
import { theme } from '../../styles/theme';

const spin = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${theme.spacing.xl};
`;

const Spinner = styled.div`
  width: 40px;
  height: 40px;
  border: 4px solid ${theme.colors.snow1};
  border-top: 4px solid ${theme.colors.frost3};
  border-radius: 50%;
  animation: ${spin} 1s linear infinite;
  margin-bottom: ${theme.spacing.md};
`;

const LoadingText = styled.p`
  color: ${theme.colors.textLight};
  margin: 0;
`;

interface LoadingIndicatorProps {
  text?: string;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ text = 'Loading...' }) => {
  return (
    <LoadingContainer>
      <Spinner />
      <LoadingText>{text}</LoadingText>
    </LoadingContainer>
  );
};

export default LoadingIndicator; 