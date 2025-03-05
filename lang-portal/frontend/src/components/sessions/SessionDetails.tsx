import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import styled from 'styled-components';
import { format } from 'date-fns';
import { theme } from '../../styles/theme';
import sessionService from '../../api/sessionService';
import { StudySessionDetail } from '../../api/types';
import LoadingIndicator from '../ui/LoadingIndicator';

const Container = styled.div`
  padding: ${theme.spacing.lg};
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing.lg};
`;

const BackLink = styled(Link)`
  color: ${theme.colors.frost3};
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
  
  &:hover {
    text-decoration: underline;
  }
`;

const Title = styled.h1`
  color: ${theme.colors.textDark};
  margin: 0;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.lg};
`;

const InfoCard = styled.div`
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.md};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const InfoLabel = styled.div`
  font-size: 0.9rem;
  color: ${theme.colors.textLight};
  margin-bottom: ${theme.spacing.xs};
`;

const InfoValue = styled.div`
  font-size: 1.2rem;
  color: ${theme.colors.textDark};
  font-weight: bold;
`;

const SectionTitle = styled.h2`
  color: ${theme.colors.textDark};
  margin: ${theme.spacing.lg} 0 ${theme.spacing.md};
  font-size: 1.5rem;
`;

const ProgressBarContainer = styled.div`
  background-color: ${theme.colors.snow1};
  border-radius: ${theme.borderRadius};
  height: 20px;
  margin-bottom: ${theme.spacing.md};
  overflow: hidden;
`;

const ProgressBarFill = styled.div<{ percentage: number }>`
  background-color: ${theme.colors.aurora4};
  height: 100%;
  width: ${props => props.percentage}%;
  transition: width 0.5s ease-in-out;
`;

const ProgressLabel = styled.div`
  font-size: 0.9rem;
  color: ${theme.colors.textDark};
  display: flex;
  justify-content: space-between;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const TableHeader = styled.th`
  padding: ${theme.spacing.md};
  text-align: left;
  background-color: ${theme.colors.polarNight1};
  color: ${theme.colors.snow0};
  font-weight: bold;
`;

const TableRow = styled.tr<{ isCorrect?: boolean }>`
  background-color: ${props => props.isCorrect ? 'rgba(163, 190, 140, 0.1)' : 'rgba(191, 97, 106, 0.1)'};
  
  &:hover {
    background-color: ${props => props.isCorrect ? 'rgba(163, 190, 140, 0.2)' : 'rgba(191, 97, 106, 0.2)'};
  }
`;

const TableCell = styled.td`
  padding: ${theme.spacing.md};
  border-bottom: 1px solid ${theme.colors.snow1};
`;

const ResultIcon = styled.span<{ isCorrect: boolean }>`
  color: ${props => props.isCorrect ? theme.colors.aurora4 : theme.colors.aurora0};
  font-size: 1.2rem;
  font-weight: bold;
`;

const WordLink = styled(Link)`
  color: ${theme.colors.frost3};
  text-decoration: none;
  font-weight: bold;
  
  &:hover {
    text-decoration: underline;
  }
`;

const GroupLink = styled(Link)`
  color: ${theme.colors.frost3};
  text-decoration: none;
  
  &:hover {
    text-decoration: underline;
  }
`;

const ErrorMessage = styled.div`
  background-color: ${theme.colors.aurora0};
  color: white;
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  margin-bottom: ${theme.spacing.md};
`;

const formatTime = (ms: number): string => {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(1)}s`;
};

const SessionDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [session, setSession] = useState<StudySessionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  useEffect(() => {
    const fetchSessionDetails = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        const data = await sessionService.getSessionById(id);
        setSession(data);
        setError(null);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchSessionDetails();
  }, [id]);
  
  if (loading) {
    return (
      <Container>
        <LoadingIndicator text="Loading study session details..." />
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container>
        <ErrorMessage>
          Error loading study session details: {error.message}
        </ErrorMessage>
      </Container>
    );
  }
  
  if (!session) {
    return (
      <Container>
        <ErrorMessage>
          Study session not found
        </ErrorMessage>
      </Container>
    );
  }
  
  return (
    <Container>
      <Header>
        <BackLink to="/sessions">← Back to Sessions</BackLink>
      </Header>
      
      <Title>{session.activity_name} Session</Title>
      
      <InfoGrid>
        <InfoCard>
          <InfoLabel>Group</InfoLabel>
          <InfoValue>
            <GroupLink to={`/groups/${session.group_id}`}>{session.group_name}</GroupLink>
          </InfoValue>
        </InfoCard>
        
        <InfoCard>
          <InfoLabel>Date & Time</InfoLabel>
          <InfoValue>{format(new Date(session.start_time), 'PPp')}</InfoValue>
        </InfoCard>
        
        <InfoCard>
          <InfoLabel>Duration</InfoLabel>
          <InfoValue>
            {formatTime(new Date(session.end_time).getTime() - new Date(session.start_time).getTime())}
          </InfoValue>
        </InfoCard>
        
        <InfoCard>
          <InfoLabel>Words Studied</InfoLabel>
          <InfoValue>{session.review_item_count}</InfoValue>
        </InfoCard>
      </InfoGrid>
      
      <SectionTitle>Performance</SectionTitle>
      
      <ProgressBarContainer>
        <ProgressBarFill percentage={session.accuracy_percentage} />
      </ProgressBarContainer>
      
      <ProgressLabel>
        <span>Accuracy: {session.accuracy_percentage.toFixed(1)}%</span>
        <span>
          {session.correct_count} correct / {session.wrong_count} incorrect
        </span>
      </ProgressLabel>
      
      <InfoCard style={{ marginTop: theme.spacing.md }}>
        <InfoLabel>Average Response Time</InfoLabel>
        <InfoValue>{formatTime(session.average_response_time_ms)}</InfoValue>
      </InfoCard>
      
      <SectionTitle>Word Results</SectionTitle>
      
      <Table>
        <thead>
          <tr>
            <TableHeader>Result</TableHeader>
            <TableHeader>Japanese</TableHeader>
            <TableHeader>Romaji</TableHeader>
            <TableHeader>English</TableHeader>
            <TableHeader>Response Time</TableHeader>
          </tr>
        </thead>
        <tbody>
          {session.word_results.map((result, index) => (
            <TableRow key={`${result.word_id}-${index}`} isCorrect={result.is_correct}>
              <TableCell>
                <ResultIcon isCorrect={result.is_correct}>
                  {result.is_correct ? '✓' : '✗'}
                </ResultIcon>
              </TableCell>
              <TableCell>
                <WordLink to={`/words/${result.word_id}`}>{result.japanese}</WordLink>
              </TableCell>
              <TableCell>{result.romaji}</TableCell>
              <TableCell>{result.english}</TableCell>
              <TableCell>{formatTime(result.response_time_ms)}</TableCell>
            </TableRow>
          ))}
        </tbody>
      </Table>
    </Container>
  );
};

export default SessionDetails; 