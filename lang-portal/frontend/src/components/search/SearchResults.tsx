import React from 'react';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import { useSearch } from '../../contexts/SearchContext';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import LoadingIndicator from '../ui/LoadingIndicator';

const ResultsContainer = styled.div<{ visible: boolean }>`
  position: absolute;
  top: 60px;
  right: 0;
  width: 400px;
  max-height: 500px;
  overflow-y: auto;
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 10;
  opacity: ${props => props.visible ? '1' : '0'};
  transform: translateY(${props => props.visible ? '0' : '-10px'});
  pointer-events: ${props => props.visible ? 'auto' : 'none'};
  transition: all 0.2s ease;
`;

const Section = styled.div`
  padding: ${theme.spacing.md};
  border-bottom: 1px solid ${theme.colors.snow1};
  
  &:last-child {
    border-bottom: none;
  }
`;

const SectionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing.sm};
`;

const SectionTitle = styled.h3`
  margin: 0;
  color: ${theme.colors.textDark};
  font-size: 1rem;
  display: flex;
  align-items: center;
  gap: ${theme.spacing.sm};
`;

const SectionIcon = styled.span`
  color: ${theme.colors.frost3};
  font-size: 1.2rem;
  width: 20px;
  height: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
`;

const SectionCount = styled.span`
  font-size: 0.8rem;
  color: ${theme.colors.textLight};
`;

const ViewAllLink = styled.a`
  font-size: 0.8rem;
  color: ${theme.colors.frost3};
  text-decoration: none;
  cursor: pointer;
  
  &:hover {
    text-decoration: underline;
  }
`;

const ResultsList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const ResultItem = styled.li`
  padding: ${theme.spacing.sm};
  cursor: pointer;
  border-radius: ${theme.borderRadius};
  
  &:hover {
    background-color: ${theme.colors.snow1};
  }
`;

const WordResult = styled(ResultItem)`
  display: grid;
  grid-template-columns: 1fr auto;
`;

const WordJapanese = styled.div`
  color: ${theme.colors.textDark};
  font-weight: bold;
`;

const WordRomaji = styled.div`
  color: ${theme.colors.textLight};
  font-size: 0.9rem;
`;

const WordEnglish = styled.div`
  color: ${theme.colors.textDark};
  text-align: right;
`;

const GroupResult = styled(ResultItem)`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const GroupName = styled.div`
  color: ${theme.colors.textDark};
  font-weight: bold;
`;

const WordCount = styled.div`
  font-size: 0.8rem;
  color: ${theme.colors.textLight};
  background-color: ${theme.colors.snow1};
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  border-radius: 12px;
`;

const SessionResult = styled(ResultItem)``;

const SessionActivity = styled.div`
  color: ${theme.colors.textDark};
  font-weight: bold;
`;

const SessionGroup = styled.div`
  color: ${theme.colors.frost3};
  font-size: 0.9rem;
`;

const SessionDate = styled.div`
  color: ${theme.colors.textLight};
  font-size: 0.8rem;
`;

const MessageContainer = styled.div`
  padding: ${theme.spacing.lg};
  text-align: center;
  color: ${theme.colors.textLight};
`;

const SearchResults: React.FC = () => {
  const { query, results, loading, error, searchVisible } = useSearch();
  const navigate = useNavigate();
  
  const handleWordClick = (wordId: string) => {
    navigate(`/words/${wordId}`);
  };
  
  const handleGroupClick = (groupId: string) => {
    navigate(`/groups/${groupId}`);
  };
  
  const handleSessionClick = (sessionId: string) => {
    navigate(`/sessions/${sessionId}`);
  };
  
  const handleViewAllWords = () => {
    navigate(`/words?search=${encodeURIComponent(query)}`);
  };
  
  const handleViewAllGroups = () => {
    navigate(`/groups?search=${encodeURIComponent(query)}`);
  };
  
  const handleViewAllSessions = () => {
    navigate(`/sessions?search=${encodeURIComponent(query)}`);
  };
  
  if (loading) {
    return (
      <ResultsContainer visible={searchVisible}>
        <MessageContainer>
          <LoadingIndicator text="Searching..." />
        </MessageContainer>
      </ResultsContainer>
    );
  }
  
  if (error) {
    return (
      <ResultsContainer visible={searchVisible}>
        <MessageContainer>
          Error: {error.message}
        </MessageContainer>
      </ResultsContainer>
    );
  }
  
  if (!results || (!results.words.total && !results.groups.total && !results.sessions.total)) {
    return (
      <ResultsContainer visible={searchVisible && query.length > 0}>
        <MessageContainer>
          {query.length > 0 ? 'No results found' : 'Type to search'}
        </MessageContainer>
      </ResultsContainer>
    );
  }
  
  return (
    <ResultsContainer visible={searchVisible && query.length > 0}>
      {results.words.total > 0 && (
        <Section>
          <SectionHeader>
            <SectionTitle>
              <SectionIcon>📚</SectionIcon> Words
              <SectionCount>({results.words.total})</SectionCount>
            </SectionTitle>
            {results.words.total > results.words.results.length && (
              <ViewAllLink onClick={handleViewAllWords}>View all</ViewAllLink>
            )}
          </SectionHeader>
          <ResultsList>
            {results.words.results.map(word => (
              <WordResult key={word.id} onClick={() => handleWordClick(word.id)}>
                <div>
                  <WordJapanese>{word.japanese}</WordJapanese>
                  <WordRomaji>{word.romaji}</WordRomaji>
                </div>
                <WordEnglish>{word.english}</WordEnglish>
              </WordResult>
            ))}
          </ResultsList>
        </Section>
      )}
      
      {results.groups.total > 0 && (
        <Section>
          <SectionHeader>
            <SectionTitle>
              <SectionIcon>📂</SectionIcon> Groups
              <SectionCount>({results.groups.total})</SectionCount>
            </SectionTitle>
            {results.groups.total > results.groups.results.length && (
              <ViewAllLink onClick={handleViewAllGroups}>View all</ViewAllLink>
            )}
          </SectionHeader>
          <ResultsList>
            {results.groups.results.map(group => (
              <GroupResult key={group.id} onClick={() => handleGroupClick(group.id)}>
                <GroupName>{group.name}</GroupName>
                <WordCount>{group.word_count} words</WordCount>
              </GroupResult>
            ))}
          </ResultsList>
        </Section>
      )}
      
      {results.sessions.total > 0 && (
        <Section>
          <SectionHeader>
            <SectionTitle>
              <SectionIcon>⏱️</SectionIcon> Study Sessions
              <SectionCount>({results.sessions.total})</SectionCount>
            </SectionTitle>
            {results.sessions.total > results.sessions.results.length && (
              <ViewAllLink onClick={handleViewAllSessions}>View all</ViewAllLink>
            )}
          </SectionHeader>
          <ResultsList>
            {results.sessions.results.map(session => (
              <SessionResult key={session.id} onClick={() => handleSessionClick(session.id)}>
                <SessionActivity>{session.activity_name}</SessionActivity>
                <SessionGroup>{session.group_name}</SessionGroup>
                <SessionDate>{format(new Date(session.start_time), 'PP')}</SessionDate>
              </SessionResult>
            ))}
          </ResultsList>
        </Section>
      )}
    </ResultsContainer>
  );
};

export default SearchResults; 