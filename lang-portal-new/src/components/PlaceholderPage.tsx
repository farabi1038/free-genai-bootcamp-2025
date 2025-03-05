import styled from 'styled-components';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
`;

const Title = styled.h1`
  margin-bottom: 20px;
`;

const Description = styled.p`
  color: #666;
  max-width: 600px;
  line-height: 1.6;
  margin-bottom: 30px;
`;

const MockBox = styled.div`
  width: 100%;
  max-width: 800px;
  height: 300px;
  background-color: #f5f5f5;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 18px;
  margin-bottom: 20px;
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