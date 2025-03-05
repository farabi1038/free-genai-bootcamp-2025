import React from 'react';
import styled from 'styled-components';
import { format, parseISO } from 'date-fns';
import { Link } from 'react-router-dom';
import { theme } from '../../styles/theme';
import { LastStudySession } from '../../api/types';
import LoadingIndicator from '../ui/LoadingIndicator';

const CardContainer = styled.div`
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.xl};
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing.lg};
`;

const CardTitle = styled.h2`
  margin: 0;
  font-size: 1.4rem;
  color: ${theme.colors.frost3};
  display: flex;
  align-items: center;
`;

const CardIcon = styled.span`
  margin-right: ${theme.spacing.sm};
  font-size: 1.4rem;
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: ${theme.colors.textLight};
  
  p {
    margin-bottom: ${theme.spacing.lg};
  }
`;

const SessionContent = styled.div`
  flex: 1;
`;

const ActivityName = styled.h3`
  font-size: 1.4rem;
  margin: 0 0 ${theme.spacing.sm} 0;
  color: ${theme.colors.textDark};
`;

const GroupName = styled(Link)`
  display: inline-block;
  font-size: 1.1rem;
  margin-bottom: ${theme.spacing.md};
  color: ${theme.colors.frost2};
  text-decoration: none;
  
  &:hover {
    color: ${theme.colors.frost3};
    text-decoration: underline;
  }
`;

const Timestamp = styled.div`
  font-size: 0.9rem;
  color: ${theme.colors.textLight};
  margin-bottom: ${theme.spacing.lg};
`;

const ResultsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${theme.spacing.md};
  margin-top: ${theme.spacing.lg};
`;

const ResultItem = styled.div<{ type: 'correct' | 'incorrect' }>`
  background-color: ${props => props.type === 'correct' 
    ? `rgba(163, 190, 140, 0.1)` // aurora4 light green 
    : `rgba(191, 97, 106, 0.1)`}; // aurora0 light red
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  text-align: center;
`;

const ResultValue = styled.div<{ type: 'correct' | 'incorrect' }>`
  font-size: 2rem;
  font-weight: bold;
  color: ${props => props.type === 'correct' 
    ? theme.colors.aurora4 
    : theme.colors.aurora0};
`;

const ResultLabel = styled.div`
  font-size: 0.9rem;
  color: ${theme.colors.textLight};
`;

const ViewSessionButton = styled(Link)`
  display: inline-block;
  margin-top: ${theme.spacing.xl};
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  background-color: ${theme.colors.frost1};
  color: white;
  text-decoration: none;
  border-radius: ${theme.borderRadius};
  transition: background-color 0.2s;
  text-align: center;
  
  &:hover {
    background-color: ${theme.colors.frost3};
  }
`;

const StartStudyingButton = styled(Link)`
  display: inline-block;
  padding: ${theme.spacing.md} ${theme.spacing.xl};
  background-color: ${theme.colors.frost3};
  color: white;
  text-decoration: none;
  border-radius: ${theme.borderRadius};
  transition: background-color 0.2s;
  text-align: center;
  font-weight: bold;
  
  &:hover {
    background-color: ${theme.colors.frost2};
  }
`;

interface LastStudySessionCardProps {
  session: LastStudySession | null;
  loading: boolean;
  error: Error | null;
}

const LastStudySessionCard: React.FC<LastStudySessionCardProps> = ({ session, loading, error }) => {
  if (loading) {
    return (
      <CardContainer>
        <CardHeader>
          <CardTitle><CardIcon>⏱️</CardIcon> Last Study Session</CardTitle>
        </CardHeader>
        <LoadingIndicator text="Loading session data..." />
      </CardContainer>
    );
  }
  
  if (error) {
    return (
      <CardContainer>
        <CardHeader>
          <CardTitle><CardIcon>⏱️</CardIcon> Last Study Session</CardTitle>
        </CardHeader>
        <EmptyState>
          <p>Error loading session data. Please try again later.</p>
        </EmptyState>
      </CardContainer>
    );
  }
  
  if (!session) {
    return (
      <CardContainer>
        <CardHeader>
          <CardTitle><CardIcon>⏱️</CardIcon> Last Study Session</CardTitle>
        </CardHeader>
        <EmptyState>
          <p>You haven't completed any study sessions yet.</p>
          <StartStudyingButton to="/study">Start Studying</StartStudyingButton>
        </EmptyState>
      </CardContainer>
    );
  }
  
  return (
    <CardContainer>
      <CardHeader>
        <CardTitle><CardIcon>⏱️</CardIcon> Last Study Session</CardTitle>
      </CardHeader>
      <SessionContent>
        <ActivityName>{session.activity}</ActivityName>
        <GroupName to={`/groups/${session.group_id}`}>{session.group}</GroupName>
        <Timestamp>{format(parseISO(session.timestamp), 'PPpp')}</Timestamp>
        
        <ResultsGrid>
          <ResultItem type="correct">
            <ResultValue type="correct">{session.correct}</ResultValue>
            <ResultLabel>Correct</ResultLabel>
          </ResultItem>
          <ResultItem type="incorrect">
            <ResultValue type="incorrect">{session.wrong}</ResultValue>
            <ResultLabel>Incorrect</ResultLabel>
          </ResultItem>
        </ResultsGrid>
      </SessionContent>
      
      <ViewSessionButton to={`/sessions/${session.group_id}`}>
        View Session Details
      </ViewSessionButton>
    </CardContainer>
  );
};

export default LastStudySessionCard; 