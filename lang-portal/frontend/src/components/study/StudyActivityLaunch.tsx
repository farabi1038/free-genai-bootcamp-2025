import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import useApi from '../../hooks/useApi';
import StudyActivityService from '../../api/studyActivityService';
import LoadingIndicator from '../ui/LoadingIndicator';

const Container = styled.div`
  max-width: 600px;
  margin: 0 auto;
`;

const FormCard = styled.div`
  background-color: ${theme.colors.card};
  border-radius: ${theme.borderRadius.md};
  box-shadow: ${theme.shadows.md};
  padding: ${theme.spacing.lg};
  border: 1px solid ${theme.colors.border};
`;

const Title = styled.h1`
  color: ${theme.colors.polar1};
  margin-bottom: ${theme.spacing.lg};
  font-size: 2.2rem;
  text-align: center;
`;

const FormGroup = styled.div`
  margin-bottom: ${theme.spacing.lg};
`;

const Label = styled.label`
  display: block;
  margin-bottom: ${theme.spacing.sm};
  font-weight: 500;
  color: ${theme.colors.polar3};
`;

const Select = styled.select`
  width: 100%;
  padding: ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.sm};
  background-color: white;
  font-size: 16px;
  color: ${theme.colors.text};
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 1em;
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.frost3};
    box-shadow: 0 0 0 2px rgba(136, 192, 208, 0.2);
  }
`;

const SubmitButton = styled.button`
  width: 100%;
  background-color: ${theme.colors.secondary};
  color: white;
  border: none;
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius.sm};
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  margin-top: ${theme.spacing.lg};
  
  &:hover {
    background-color: #8CAA7A;
  }
  
  &:disabled {
    background-color: ${theme.colors.snow1};
    color: ${theme.colors.textLight};
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  color: ${theme.colors.aurora1};
  background-color: #FFF0F0;
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius.sm};
  margin-bottom: ${theme.spacing.lg};
  border: 1px solid #FFDCDC;
`;

// Mock groups for select dropdown
const mockGroups = [
  { id: '1', name: 'Basic Japanese' },
  { id: '2', name: 'Food Words' },
  { id: '3', name: 'Travel Words' },
  { id: '4', name: 'JLPT N5 Vocabulary' },
  { id: '5', name: 'Common Verbs' }
];

const StudyActivityLaunch = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [selectedGroup, setSelectedGroup] = useState('');
  
  const { data: activity, loading: loadingActivity, error: activityError, execute: fetchActivity } = useApi(
    () => StudyActivityService.getActivityById(id || '')
  );
  
  const { 
    data: launchResult, 
    loading: launching, 
    error: launchError, 
    execute: launchActivity 
  } = useApi(
    () => StudyActivityService.launchActivity(id || '', selectedGroup)
  );
  
  useEffect(() => {
    if (id) {
      fetchActivity();
    }
  }, [id, fetchActivity]);
  
  useEffect(() => {
    if (launchResult) {
      // Open the activity URL in a new tab
      window.open(launchResult.url, '_blank');
      
      // Redirect to study session details
      navigate(`/sessions/${launchResult.study_session_id}`);
    }
  }, [launchResult, navigate]);
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (id && selectedGroup) {
      launchActivity();
    }
  };
  
  if (loadingActivity) {
    return <LoadingIndicator text="Loading activity..." />;
  }
  
  if (activityError) {
    return <ErrorMessage>Error: {activityError.message}</ErrorMessage>;
  }
  
  if (!activity) {
    return <ErrorMessage>Activity not found</ErrorMessage>;
  }
  
  return (
    <Container>
      <Title>Launch {activity.name}</Title>
      {launchError && <ErrorMessage>Error: {launchError.message}</ErrorMessage>}
      <FormCard>
        <form onSubmit={handleSubmit}>
          <FormGroup>
            <Label htmlFor="group">Select Word Group</Label>
            <Select
              id="group"
              value={selectedGroup}
              onChange={(e) => setSelectedGroup(e.target.value)}
              required
            >
              <option value="">Select a group...</option>
              {mockGroups.map(group => (
                <option key={group.id} value={group.id}>
                  {group.name}
                </option>
              ))}
            </Select>
          </FormGroup>
          <SubmitButton type="submit" disabled={!selectedGroup || launching}>
            {launching ? 'Launching...' : 'Launch Now'}
          </SubmitButton>
        </form>
      </FormCard>
    </Container>
  );
};

export default StudyActivityLaunch; 