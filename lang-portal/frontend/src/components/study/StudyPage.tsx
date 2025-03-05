import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import FlashcardActivity from './activities/FlashcardActivity';
import MultipleChoiceActivity from './activities/MultipleChoiceActivity';
import TypingActivity from './activities/TypingActivity';
import MatchingActivity from './activities/MatchingActivity';
import groupService from '../../api/groupService';
import { Word, Group } from '../../api/types';
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

const GroupInfo = styled.div`
  display: flex;
  align-items: center;
  gap: ${theme.spacing.md};
`;

const GroupName = styled.span`
  color: ${theme.colors.frost3};
  font-weight: bold;
`;

const ErrorMessage = styled.div`
  background-color: ${theme.colors.aurora0};
  color: white;
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  margin-bottom: ${theme.spacing.md};
`;

const BackButton = styled.button`
  background-color: transparent;
  color: ${theme.colors.frost3};
  border: 1px solid ${theme.colors.frost3};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: ${theme.colors.snow1};
  }
`;

const StudyPage: React.FC = () => {
  const { activityType } = useParams<{ activityType: string }>();
  const location = useLocation();
  const navigate = useNavigate();
  const [words, setWords] = useState<Word[]>([]);
  const [group, setGroup] = useState<Group | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  // Get groupId from URL query parameters
  const queryParams = new URLSearchParams(location.search);
  const groupId = queryParams.get('groupId');
  
  useEffect(() => {
    const fetchGroupAndWords = async () => {
      if (!groupId) {
        setError(new Error('No group selected. Please choose a group to study.'));
        setLoading(false);
        return;
      }
      
      try {
        setLoading(true);
        
        // Fetch group details
        const groupData = await groupService.getGroupById(groupId);
        setGroup(groupData);
        
        // Fetch words for the group
        const wordsData = await groupService.getWordsByGroupId(groupId);
        
        // Check if we have words
        if (!wordsData || wordsData.length === 0) {
          setError(new Error('This group has no words. Please select a different group.'));
        } else {
          setWords(wordsData);
          console.log(`Loaded ${wordsData.length} words for group ${groupId}`);
        }
        
        setError(null);
      } catch (err) {
        console.error("Error loading study data:", err);
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchGroupAndWords();
  }, [groupId]);
  
  if (loading) {
    return (
      <Container>
        <LoadingIndicator text="Loading study session..." />
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container>
        <Header>
          <Title>Study Session</Title>
          <BackButton onClick={() => navigate('/study')}>Back to Activities</BackButton>
        </Header>
        <ErrorMessage>
          {error.message}
        </ErrorMessage>
      </Container>
    );
  }
  
  if (!activityType) {
    return (
      <Container>
        <Header>
          <Title>Study Session</Title>
          <BackButton onClick={() => navigate('/study')}>Back to Activities</BackButton>
        </Header>
        <ErrorMessage>
          No activity type specified.
        </ErrorMessage>
      </Container>
    );
  }
  
  if (!group) {
    return (
      <Container>
        <Header>
          <Title>Study Session</Title>
          <BackButton onClick={() => navigate('/study')}>Back to Activities</BackButton>
        </Header>
        <ErrorMessage>
          Group not found.
        </ErrorMessage>
      </Container>
    );
  }
  
  // Format title based on activity type
  const getActivityTitle = () => {
    switch (activityType) {
      case 'flashcards': return 'Flashcards';
      case 'multiple-choice': return 'Multiple Choice';
      case 'typing': return 'Typing Practice';
      case 'matching': return 'Matching Game';
      default: return 'Study Session';
    }
  };
  
  const renderActivity = () => {
    // Make sure we have the necessary components
    const activityProps = { words, groupId: group.id };
    
    switch (activityType) {
      case 'flashcards':
        return <FlashcardActivity {...activityProps} />;
      case 'multiple-choice':
        return <MultipleChoiceActivity {...activityProps} />;
      case 'typing':
        // Check if TypingActivity exists
        if (typeof TypingActivity !== 'undefined') {
          return <TypingActivity {...activityProps} />;
        }
        return <div>Typing Activity is not available.</div>;
      case 'matching':
        // Check if MatchingActivity exists
        if (typeof MatchingActivity !== 'undefined') {
          return <MatchingActivity {...activityProps} />;
        }
        return <div>Matching Activity is not available.</div>;
      default:
        return <div>Unknown activity type: {activityType}</div>;
    }
  };
  
  return (
    <Container>
      <Header>
        <div>
          <Title>{getActivityTitle()}</Title>
          <GroupInfo>
            Studying: <GroupName>{group.name}</GroupName>
          </GroupInfo>
        </div>
        <BackButton onClick={() => navigate('/study')}>Back to Activities</BackButton>
      </Header>
      
      {renderActivity()}
    </Container>
  );
};

export default StudyPage; 