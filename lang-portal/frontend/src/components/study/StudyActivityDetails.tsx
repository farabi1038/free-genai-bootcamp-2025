import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import useApi from '../../hooks/useApi';
import StudyActivityService from '../../api/studyActivityService';
import LoadingIndicator from '../ui/LoadingIndicator';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${theme.spacing.lg};
`;

const ActivityHeader = styled.div`
  display: flex;
  gap: ${theme.spacing.lg};
  align-items: flex-start;
  margin-bottom: ${theme.spacing.lg};
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const ThumbnailContainer = styled.div`
  width: 300px;
  height: 200px;
  border-radius: ${theme.borderRadius.md};
  overflow: hidden;
  flex-shrink: 0;
  
  @media (max-width: 768px) {
    width: 100%;
    height: auto;
    aspect-ratio: 3/2;
  }
`;

const Thumbnail = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
`;

const ActivityInfo = styled.div`
  flex-grow: 1;
`;

const Title = styled.h1`
  color: ${theme.colors.polar1};
  margin-bottom: ${theme.spacing.lg};
`;

const StudyActivityDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const { data: activity, loading, error, execute: fetchActivity } = useApi(
    () => StudyActivityService.getActivityById(id),
    [id]
  );

  useEffect(() => {
    fetchActivity();
  }, [fetchActivity]);

  if (loading) {
    return <LoadingIndicator text="Loading study activity details..." />;
  }

  if (error) {
    return <p>Error: {error.message}</p>;
  }

  return (
    <Container>
      <ActivityHeader>
        <ThumbnailContainer>
          <Thumbnail src={activity?.thumbnail_url} alt={activity?.name} />
        </ThumbnailContainer>
        <ActivityInfo>
          <Title>{activity?.name}</Title>
          {/* Add more activity details here */}
        </ActivityInfo>
      </ActivityHeader>
      {/* Add other components or content related to the study activity */}
    </Container>
  );
};

export default StudyActivityDetails; 