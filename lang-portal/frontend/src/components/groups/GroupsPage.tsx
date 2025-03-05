import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import groupService from '../../api/groupService';
import { Group } from '../../api/types';
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

const GroupsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: ${theme.spacing.lg};
`;

const GroupCard = styled(Link)`
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.lg};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-decoration: none;
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
`;

const GroupName = styled.h2`
  color: ${theme.colors.textDark};
  margin: 0 0 ${theme.spacing.sm} 0;
  font-size: 1.5rem;
`;

const WordCount = styled.div`
  color: ${theme.colors.textLight};
  font-size: 0.9rem;
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

const GroupLink = styled(Link)`
  color: ${theme.colors.frost3};
  text-decoration: none;
  font-weight: bold;
  
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

const ErrorMessage = styled.div`
  background-color: ${theme.colors.aurora0};
  color: white;
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  margin-bottom: ${theme.spacing.md};
`;

const GroupsPage: React.FC = () => {
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  
  useEffect(() => {
    const fetchGroups = async () => {
      try {
        setLoading(true);
        const data = await groupService.getAllGroups();
        setGroups(data);
        setError(null);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchGroups();
  }, []);
  
  if (loading) {
    return (
      <Container>
        <LoadingIndicator text="Loading groups..." />
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container>
        <ErrorMessage>
          Error loading groups: {error.message}
        </ErrorMessage>
      </Container>
    );
  }
  
  return (
    <Container>
      <Header>
        <Title>Word Groups</Title>
      </Header>
      
      {groups.length === 0 ? (
        <p>No groups available.</p>
      ) : (
        <>
          <Table>
            <thead>
              <tr>
                <TableHeader>Group Name</TableHeader>
                <TableHeader>Word Count</TableHeader>
              </tr>
            </thead>
            <tbody>
              {groups.map(group => (
                <TableRow key={group.id}>
                  <TableCell>
                    <GroupLink to={`/groups/${group.id}`}>{group.name}</GroupLink>
                  </TableCell>
                  <TableCell>{group.word_count}</TableCell>
                </TableRow>
              ))}
            </tbody>
          </Table>
        </>
      )}
    </Container>
  );
};

export default GroupsPage; 