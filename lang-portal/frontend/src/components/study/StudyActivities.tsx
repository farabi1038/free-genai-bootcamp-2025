import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import useApi from '../../hooks/useApi';
import StudyActivityService from '../../api/studyActivityService';
import StudyActivityCard from './StudyActivityCard';
import LoadingIndicator from '../ui/LoadingIndicator';

const PageHeading = styled.h1`
  color: ${theme.colors.polar1};
  margin-bottom: ${theme.spacing.lg};
  font-size: 2.2rem;
`;

const ActivitiesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: ${theme.spacing.lg};
`;

const ErrorMessage = styled.div`
  color: ${theme.colors.aurora1};
  background-color: #FFF0F0;
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius.sm};
  margin-bottom: ${theme.spacing.lg};
  border: 1px solid #FFDCDC;
`;

const StudyActivities = () => {
  const { data: activities, loading, error, execute: fetchActivities } = useApi(
    StudyActivityService.getAllActivities
  );
  
  useEffect(() => {
    fetchActivities();
  }, [fetchActivities]);
  
  if (loading) {
    return <LoadingIndicator text="Loading study activities..." />;
  }
  
  if (error) {
    return <ErrorMessage>Error: {error.message}</ErrorMessage>;
  }
  
  return (
    <>
      <PageHeading>Study Activities</PageHeading>
      {activities?.length ? (
        <ActivitiesGrid>
          {activities.map(activity => (
            <StudyActivityCard key={activity.id} activity={activity} />
          ))}
        </ActivitiesGrid>
      ) : (
        <p>No study activities available. Please check back later.</p>
      )}
    </>
  );
};

export default StudyActivities; 