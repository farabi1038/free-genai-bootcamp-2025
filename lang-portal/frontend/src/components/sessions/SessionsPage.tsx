import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { format } from 'date-fns';
import { theme } from '../../styles/theme';
import sessionService from '../../api/sessionService';
import { StudySession } from '../../api/types';
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

const Title = styled.h1`
  color: ${theme.colors.textDark};
  margin: 0;
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

const TableRow = styled.tr`
  &:nth-child(even) {
    background-color: ${theme.colors.snow1};
  }
  
  &:hover {
    background-color: ${theme.colors.frost0};
  }
`;

const TableCell = styled.td`
  padding: ${theme.spacing.md};
  border-bottom: 1px solid ${theme.colors.snow1};
`;

const SessionLink = styled(Link)`
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

const PaginationContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: ${theme.spacing.lg};
  gap: ${theme.spacing.md};
`;

const PageButton = styled.button`
  background-color: ${theme.colors.frost2};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  font-size: 0.9rem;
  cursor: pointer;
  
  &:hover {
    background-color: ${theme.colors.frost3};
  }
  
  &:disabled {
    background-color: ${theme.colors.disabled};
    cursor: not-allowed;
  }
`;

const AccuracyBadge = styled.span<{ accuracy: number }>`
  display: inline-block;
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  border-radius: ${theme.borderRadius};
  font-size: 0.8rem;
  font-weight: bold;
  color: white;
  background-color: ${props => {
    if (props.accuracy >= 80) return theme.colors.aurora4;
    if (props.accuracy >= 60) return theme.colors.aurora3;
    if (props.accuracy >= 40) return theme.colors.aurora2;
    return theme.colors.aurora0;
  }};
`;

const ErrorMessage = styled.div`
  background-color: ${theme.colors.aurora0};
  color: white;
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  margin-bottom: ${theme.spacing.md};
`;

const SessionsPage: React.FC = () => {
  const [sessions, setSessions] = useState<StudySession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalSessions, setTotalSessions] = useState(0);
  const sessionsPerPage = 10;
  
  useEffect(() => {
    const fetchSessions = async () => {
      try {
        setLoading(true);
        const data = await sessionService.getAllSessions(currentPage, sessionsPerPage);
        setSessions(data.sessions);
        setTotalSessions(data.total);
        setError(null);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchSessions();
  }, [currentPage]);
  
  if (loading && sessions.length === 0) {
    return (
      <Container>
        <LoadingIndicator text="Loading study sessions..." />
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container>
        <ErrorMessage>
          Error loading study sessions: {error.message}
        </ErrorMessage>
      </Container>
    );
  }
  
  return (
    <Container>
      <Header>
        <Title>Study Sessions History</Title>
      </Header>
      
      {sessions.length === 0 ? (
        <p>No study sessions available.</p>
      ) : (
        <>
          <Table>
            <thead>
              <tr>
                <TableHeader>Activity</TableHeader>
                <TableHeader>Group</TableHeader>
                <TableHeader>Date</TableHeader>
                <TableHeader>Words</TableHeader>
                <TableHeader>Accuracy</TableHeader>
              </tr>
            </thead>
            <tbody>
              {sessions.map(session => {
                const accuracy = (session.correct_count / session.review_item_count) * 100;
                
                return (
                  <TableRow key={session.id}>
                    <TableCell>
                      <SessionLink to={`/sessions/${session.id}`}>{session.activity_name}</SessionLink>
                    </TableCell>
                    <TableCell>
                      <GroupLink to={`/groups/${session.group_id}`}>{session.group_name}</GroupLink>
                    </TableCell>
                    <TableCell>{format(new Date(session.start_time), 'PPp')}</TableCell>
                    <TableCell>{session.review_item_count}</TableCell>
                    <TableCell>
                      <AccuracyBadge accuracy={accuracy}>
                        {accuracy.toFixed(0)}%
                      </AccuracyBadge>
                    </TableCell>
                  </TableRow>
                );
              })}
            </tbody>
          </Table>
          
          <PaginationContainer>
            <PageButton 
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
            >
              Previous
            </PageButton>
            <span>Page {currentPage} of {Math.ceil(totalSessions / sessionsPerPage)}</span>
            <PageButton 
              onClick={() => setCurrentPage(prev => prev + 1)}
              disabled={currentPage * sessionsPerPage >= totalSessions}
            >
              Next
            </PageButton>
          </PaginationContainer>
        </>
      )}
    </Container>
  );
};

export default SessionsPage; 