import styled from 'styled-components';
import { theme } from '../styles/theme';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: ${theme.spacing.xl};
  text-align: center;
`;

const Title = styled.h1`
  margin-bottom: ${theme.spacing.lg};
  color: ${theme.colors.polar1};
  font-size: 2.2rem;
`;

const Description = styled.p`
  color: ${theme.colors.textLight};
  max-width: 600px;
  line-height: 1.6;
  margin-bottom: ${theme.spacing.xl};
`;

const MockBox = styled.div`
  width: 100%;
  max-width: 800px;
  height: 300px;
  background-color: ${theme.colors.snow1};
  border-radius: ${theme.borderRadius.md};
  display: flex;
  align-items: center;
  justify-content: center;
  color: ${theme.colors.textLight};
  font-size: 18px;
  margin-bottom: ${theme.spacing.lg};
  border: 1px solid ${theme.colors.border};
`;

interface PlaceholderPageProps {
  title: string;
  description?: string;
}

const PlaceholderPage: React.FC<PlaceholderPageProps> = ({ 
  title, 
  description = 'This page is under construction and will be implemented in a future version.' 
}) => {
  return (
    <Container>
      <Title>{title}</Title>
      <Description>{description}</Description>
      <MockBox>Content coming soon</MockBox>
    </Container>
  );
};

export default PlaceholderPage; 