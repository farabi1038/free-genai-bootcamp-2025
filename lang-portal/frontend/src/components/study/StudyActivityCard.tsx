import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import { StudyActivity } from '../../api/types';

const Card = styled.div`
  background-color: ${theme.colors.card};
  border-radius: ${theme.borderRadius.md};
  box-shadow: ${theme.shadows.md};
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 1px solid ${theme.colors.border};
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: ${theme.shadows.lg};
  }
`;

const Thumbnail = styled.div<{ imageUrl: string }>`
  height: 180px;
  background-image: url(${props => props.imageUrl});
  background-size: cover;
  background-position: center;
`;

const Content = styled.div`
  padding: ${theme.spacing.lg};
  flex: 1;
  display: flex;
  flex-direction: column;
`;

const Title = styled.h3`
  margin: 0 0 ${theme.spacing.md} 0;
  color: ${theme.colors.text};
`;

const ButtonContainer = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
  margin-top: auto;
  padding-top: ${theme.spacing.md};
`;

const LaunchButton = styled.button`
  background-color: ${theme.colors.secondary};
  color: white;
  border: none;
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border-radius: ${theme.borderRadius.sm};
  font-weight: 500;
  cursor: pointer;
  &:hover {
    background-color: #8CAA7A;
  }
`;

const DetailsButton = styled.button`
  background-color: transparent;
  color: ${theme.colors.frost4};
  border: 1px solid ${theme.colors.frost4};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border-radius: ${theme.borderRadius.sm};
  font-weight: 500;
  cursor: pointer;
  &:hover {
    background-color: rgba(94, 129, 172, 0.1);
  }
`;

interface StudyActivityCardProps {
  activity: StudyActivity;
}

const StudyActivityCard: React.FC<StudyActivityCardProps> = ({ activity }) => {
  const navigate = useNavigate();
  
  const handleLaunch = () => {
    navigate(`/study/${activity.id}/launch`);
  };
  
  const handleDetails = () => {
    navigate(`/study/${activity.id}`);
  };
  
  return (
    <Card>
      <Thumbnail imageUrl={activity.thumbnail_url} />
      <Content>
        <Title>{activity.name}</Title>
        <ButtonContainer>
          <LaunchButton onClick={handleLaunch}>Launch</LaunchButton>
          <DetailsButton onClick={handleDetails}>Details</DetailsButton>
        </ButtonContainer>
      </Content>
    </Card>
  );
};

export default StudyActivityCard; 