import { useEffect } from 'react';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import useApi from '../../hooks/useApi';
import GroupService from '../../api/groupService';
import GroupCard from './GroupCard';
import LoadingIndicator from '../ui/LoadingIndicator';

const PageHeading = styled.h1`
  color: ${theme.colors.polar1};
  margin-bottom: ${theme.spacing.lg};
  font-size: 2.2rem;
`;

const GroupsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
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

const SearchContainer = styled.div`
  margin-bottom: ${theme.spacing.lg};
`;

const SearchInput = styled.input`
  padding: ${theme.spacing.md};
  border: 1px solid ${theme.colors.border};
  border-radius: ${theme.borderRadius.sm};
  width: 100%;
  max-width: 400px;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.frost3};
    box-shadow: 0 0 0 2px rgba(136, 192, 208, 0.2);
  }
`;

const Groups = () => {
  const { data: groups, loading, error, execute: fetchGroups } = useApi(
    GroupService.getAllGroups
  );
  
  useEffect(() => {
    fetchGroups();
  }, [fetchGroups]);
  
  if (loading) {
    return <LoadingIndicator text="Loading groups..." />;
  }
  
  if (error) {
    return <ErrorMessage>Error: {error.message}</ErrorMessage>;
  }
  
  return (
    <>
      <PageHeading>Word Groups</PageHeading>
      <SearchContainer>
        <SearchInput 
          type="text" 
          placeholder="Search groups..." 
          disabled // Will implement search functionality later
        />
      </SearchContainer>
      {groups?.length ? (
        <GroupsGrid>
          {groups.map(group => (
            <GroupCard key={group.id} group={group} />
          ))}
        </GroupsGrid>
      ) : (
        <p>No groups available. Create a group to organize your vocabulary words.</p>
      )}
    </>
  );
};

export default Groups; 