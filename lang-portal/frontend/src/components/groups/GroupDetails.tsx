import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import styled from 'styled-components';
import { format } from 'date-fns';
import { theme } from '../../styles/theme';
import groupService from '../../api/groupService';
import { Group, Word, StudySession } from '../../api/types';
import LoadingIndicator from '../ui/LoadingIndicator';

const Container = styled.div`
  padding: ${theme.spacing.lg};
  max-width: 1200px;
  margin: 0 auto;
`;

const GroupHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing.lg};
`;

const Title = styled.h1`
  color: ${theme.colors.textDark};
  margin: 0;
`;

const WordCount = styled.span`
  background-color: ${theme.colors.frost2};
  color: white;
  padding: ${theme.spacing.xs} ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  font-size: 0.9rem;
`;

const TabsContainer = styled.div`
  display: flex;
  margin-bottom: ${theme.spacing.lg};
`;

const Tab = styled.div<{ active: boolean }>`
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  background-color: ${props => props.active ? theme.colors.snow0 : theme.colors.snow1};
  color: ${props => props.active ? theme.colors.textDark : theme.colors.textLight};
  border-radius: ${theme.borderRadius} ${theme.borderRadius} 0 0;
  cursor: pointer;
  font-weight: ${props => props.active ? 'bold' : 'normal'};
  
  &:hover {
    background-color: ${props => props.active ? theme.colors.snow0 : theme.colors.snow2};
  }
`;

const Card = styled.div`
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.lg};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.th`
  padding: ${theme.spacing.md};
  text-align: left;
  border-bottom: 2px solid ${theme.colors.frost1};
  color: ${theme.colors.textDark};
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

const JapaneseWord = styled(Link)`
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

const GroupDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<'words' | 'sessions'>('words');
  const [group, setGroup] = useState<Group | null>(null);
  const [words, setWords] = useState<Word[]>([]);
  const [sessions, setSessions] = useState<StudySession[]>([]);
  const [wordsPage, setWordsPage] = useState(1);
  const [sessionsPage, setSessionsPage] = useState(1);
  const [loadingGroup, setLoadingGroup] = useState(true);
  const [loadingWords, setLoadingWords] = useState(false);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [groupError, setGroupError] = useState<Error | null>(null);
  const [wordsError, setWordsError] = useState<Error | null>(null);
  const [sessionsError, setSessionsError] = useState<Error | null>(null);
  
  // Fetch group data
  const fetchGroup = useCallback(async () => {
    if (!id) return;
    
    try {
      setLoadingGroup(true);
      const data = await groupService.getGroupById(id);
      setGroup(data);
      setGroupError(null);
    } catch (err) {
      setGroupError(err as Error);
    } finally {
      setLoadingGroup(false);
    }
  }, [id]);
  
  // Fetch words in group
  const fetchWords = useCallback(async () => {
    if (!id) return;
    
    try {
      setLoadingWords(true);
      const data = await groupService.getWordsByGroupId(id);
      setWords(data);
      setWordsError(null);
    } catch (err) {
      setWordsError(err as Error);
    } finally {
      setLoadingWords(false);
    }
  }, [id]);
  
  // Fetch study sessions for the group
  const fetchSessions = useCallback(async () => {
    if (!id) return;
    
    try {
      setLoadingSessions(true);
      const data = await groupService.getStudySessionsByGroupId(id);
      setSessions(data);
      setSessionsError(null);
    } catch (err) {
      setSessionsError(err as Error);
    } finally {
      setLoadingSessions(false);
    }
  }, [id]);
  
  // Load group data when component mounts
  useEffect(() => {
    fetchGroup();
  }, [fetchGroup]);
  
  // Load words when viewing the words tab
  useEffect(() => {
    if (activeTab === 'words') {
      fetchWords();
    }
  }, [activeTab, fetchWords]);
  
  // Load study sessions when viewing the sessions tab
  useEffect(() => {
    if (activeTab === 'sessions') {
      fetchSessions();
    }
  }, [activeTab, fetchSessions]);
  
  if (loadingGroup && !group) {
    return (
      <Container>
        <LoadingIndicator text="Loading group data..." />
      </Container>
    );
  }
  
  if (groupError) {
    return (
      <Container>
        <ErrorMessage>
          Error loading group: {groupError.message}
        </ErrorMessage>
      </Container>
    );
  }
  
  if (!group) {
    return (
      <Container>
        <ErrorMessage>
          Group not found
        </ErrorMessage>
      </Container>
    );
  }
  
  return (
    <Container>
      <GroupHeader>
        <Title>{group.name}</Title>
        <WordCount>{group.word_count} {group.word_count === 1 ? 'word' : 'words'}</WordCount>
      </GroupHeader>
      
      <TabsContainer>
        <Tab 
          active={activeTab === 'words'} 
          onClick={() => setActiveTab('words')}
        >
          Words
        </Tab>
        <Tab 
          active={activeTab === 'sessions'} 
          onClick={() => setActiveTab('sessions')}
        >
          Study Sessions
        </Tab>
      </TabsContainer>
      
      {activeTab === 'words' && (
        <Card>
          {loadingWords ? (
            <LoadingIndicator text="Loading words..." />
          ) : wordsError ? (
            <ErrorMessage>
              Error loading words: {wordsError.message}
            </ErrorMessage>
          ) : words.length === 0 ? (
            <p>No words in this group.</p>
          ) : (
            <>
              <Table>
                <thead>
                  <tr>
                    <TableHeader>Japanese</TableHeader>
                    <TableHeader>Romaji</TableHeader>
                    <TableHeader>English</TableHeader>
                    <TableHeader>Correct</TableHeader>
                    <TableHeader>Wrong</TableHeader>
                  </tr>
                </thead>
                <tbody>
                  {words.map(word => (
                    <TableRow key={word.id}>
                      <TableCell>
                        <JapaneseWord to={`/words/${word.id}`}>{word.japanese}</JapaneseWord>
                      </TableCell>
                      <TableCell>{word.romaji}</TableCell>
                      <TableCell>{word.english}</TableCell>
                      <TableCell>{word.correct_count}</TableCell>
                      <TableCell>{word.wrong_count}</TableCell>
                    </TableRow>
                  ))}
                </tbody>
              </Table>
              
              <PaginationContainer>
                <PageButton 
                  onClick={() => setWordsPage(prev => Math.max(prev - 1, 1))} 
                  disabled={wordsPage === 1}
                >
                  Previous
                </PageButton>
                <span>Page {wordsPage}</span>
                <PageButton 
                  onClick={() => setWordsPage(prev => prev + 1)} 
                  disabled={words.length < 100} // Assuming 100 items per page
                >
                  Next
                </PageButton>
              </PaginationContainer>
            </>
          )}
        </Card>
      )}
      
      {activeTab === 'sessions' && (
        <Card>
          {loadingSessions ? (
            <LoadingIndicator text="Loading study sessions..." />
          ) : sessionsError ? (
            <ErrorMessage>
              Error loading sessions: {sessionsError.message}
            </ErrorMessage>
          ) : sessions.length === 0 ? (
            <p>No study sessions for this group yet.</p>
          ) : (
            <>
              <Table>
                <thead>
                  <tr>
                    <TableHeader>ID</TableHeader>
                    <TableHeader>Activity</TableHeader>
                    <TableHeader>Start Time</TableHeader>
                    <TableHeader>End Time</TableHeader>
                    <TableHeader>Words</TableHeader>
                  </tr>
                </thead>
                <tbody>
                  {sessions.map(session => (
                    <TableRow key={session.id}>
                      <TableCell>
                        <Link to={`/sessions/${session.id}`}>{session.id}</Link>
                      </TableCell>
                      <TableCell>{session.activity_name}</TableCell>
                      <TableCell>{format(new Date(session.start_time), 'PPp')}</TableCell>
                      <TableCell>{format(new Date(session.end_time), 'PPp')}</TableCell>
                      <TableCell>{session.review_item_count}</TableCell>
                    </TableRow>
                  ))}
                </tbody>
              </Table>
              
              <PaginationContainer>
                <PageButton 
                  onClick={() => setSessionsPage(prev => Math.max(prev - 1, 1))} 
                  disabled={sessionsPage === 1}
                >
                  Previous
                </PageButton>
                <span>Page {sessionsPage}</span>
                <PageButton 
                  onClick={() => setSessionsPage(prev => prev + 1)} 
                  disabled={sessions.length < 100} // Assuming 100 items per page
                >
                  Next
                </PageButton>
              </PaginationContainer>
            </>
          )}
        </Card>
      )}
    </Container>
  );
};

export default GroupDetails; 