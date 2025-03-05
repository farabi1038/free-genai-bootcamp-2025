import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../../styles/theme';

const Container = styled.div`
  padding: ${theme.spacing.xl};
  text-align: center;
`;

const Title = styled.h1`
  color: ${theme.colors.textDark};
  margin-bottom: ${theme.spacing.lg};
`;

const Message = styled.p`
  color: ${theme.colors.textLight};
  margin-bottom: ${theme.spacing.xl};
`;

const HomeLink = styled(Link)`
  display: inline-block;
  background-color: ${theme.colors.frost3};
  color: white;
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  border-radius: ${theme.borderRadius};
  text-decoration: none;
  
  &:hover {
    background-color: ${theme.colors.frost2};
  }
`;

const NotFound: React.FC = () => {
  return (
    <Container>
      <Title>404 - Page Not Found</Title>
      <Message>
        The page you are looking for does not exist or has been moved.
      </Message>
      <HomeLink to="/">Return to Home</HomeLink>
    </Container>
  );
};

export default NotFound; 