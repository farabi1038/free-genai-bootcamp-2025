import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
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

const Title = styled.h1`
  color: ${theme.colors.textDark};
  margin-bottom: ${theme.spacing.xl};
`;

const ActivitiesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: ${theme.spacing.lg};
  margin-bottom: ${theme.spacing.xl};
`;

const ActivityCard = styled.div<{ selected: boolean }>`
  background-color: ${props => props.selected ? theme.colors.frost0 : theme.colors.snow0};
  border: 2px solid ${props => props.selected ? theme.colors.frost3 : 'transparent'};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.lg};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
`;

const ActivityIcon = styled.div`
  font-size: 2.5rem;
  margin-bottom: ${theme.spacing.md};
  color: ${theme.colors.frost3};
`;

const ActivityName = styled.h3`
  color: ${theme.colors.textDark};
  margin-bottom: ${theme.spacing.sm};
`;

const ActivityDescription = styled.p`
  color: ${theme.colors.textLight};
  font-size: 0.9rem;
`;

const GroupsSection = styled.div`
  margin-top: ${theme.spacing.xl};
  display: ${props => props.hidden ? 'none' : 'block'};
`;

const GroupsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: ${theme.spacing.md};
  margin-top: ${theme.spacing.md};
`;

const GroupCard = styled.div<{ selected: boolean }>`
  background-color: ${props => props.selected ? theme.colors.frost2 : theme.colors.snow0};
  color: ${props => props.selected ? theme.colors.snow0 : theme.colors.textDark};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.md};
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background-color: ${props => props.selected ? theme.colors.frost3 : theme.colors.snow1};
  }
`;

const GroupName = styled.h3`
  margin-bottom: ${theme.spacing.xs};
`;

const GroupInfo = styled.p`
  font-size: 0.9rem;
  color: ${props => props.color || theme.colors.textLight};
`;

const StartButton = styled.button`
  background-color: ${theme.colors.success};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.md} ${theme.spacing.xl};
  font-size: 1rem;
  font-weight: bold;
  margin-top: ${theme.spacing.xl};
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: ${theme.colors.aurora4};
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

const activities = [
  {
    id: 'flashcards',
    name: 'Flashcards',
    description: 'Review words with flashcards to improve recognition and recall.',
    icon: '🎴'
  },
  {
    id: 'multiple-choice',
    name: 'Multiple Choice',
    description: 'Test your knowledge with multiple choice questions.',
    icon: '📝'
  },
  {
    id: 'typing',
    name: 'Typing Practice',
    description: 'Strengthen recall by typing the correct answers.',
    icon: '⌨️'
  },
  {
    id: 'matching',
    name: 'Matching Game',
    description: 'Match related words and translations in a memory-style game.',
    icon: '🔄'
  }
];

const ActivitySelector: React.FC = () => {
  const [selectedActivity, setSelectedActivity] = useState<string | null>(null);
  const [selectedGroupIds, setSelectedGroupIds] = useState<Set<string>>(new Set());
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const navigate = useNavigate();
  
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
  
  const handleActivitySelect = (activityId: string) => {
    setSelectedActivity(activityId);
  };
  
  const toggleGroup = (groupId: string) => {
    const newSelectedGroups = new Set(selectedGroupIds);
    if (newSelectedGroups.has(groupId)) {
      newSelectedGroups.delete(groupId);
    } else {
      newSelectedGroups.add(groupId);
    }
    setSelectedGroupIds(newSelectedGroups);
  };
  
  const handleStartActivity = () => {
    if (!selectedActivity || selectedGroupIds.size === 0) return;
    
    // Convert set to array for URL
    const groupIdsParam = Array.from(selectedGroupIds).join(',');
    navigate(`/study/${selectedActivity}?groups=${groupIdsParam}`);
  };
  
  if (loading) {
    return (
      <Container>
        <LoadingIndicator text="Loading study options..." />
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container>
        <Title>Study Activities</Title>
        <ErrorMessage>
          Error loading groups: {error.message}
        </ErrorMessage>
      </Container>
    );
  }
  
  return (
    <Container>
      <Title>Choose a Study Activity</Title>
      
      <ActivitiesGrid>
        {activities.map(activity => (
          <ActivityCard 
            key={activity.id}
            selected={selectedActivity === activity.id}
            onClick={() => handleActivitySelect(activity.id)}
          >
            <ActivityIcon>{activity.icon}</ActivityIcon>
            <ActivityName>{activity.name}</ActivityName>
            <ActivityDescription>{activity.description}</ActivityDescription>
          </ActivityCard>
        ))}
      </ActivitiesGrid>
      
      <GroupsSection hidden={!selectedActivity}>
        <h2>Select Groups to Study</h2>
        <p>Choose one or more groups to include in your study session:</p>
        
        <GroupsGrid>
          {groups.map(group => (
            <GroupCard
              key={group.id}
              selected={selectedGroupIds.has(group.id)}
              onClick={() => toggleGroup(group.id)}
            >
              <GroupName>{group.name}</GroupName>
              <GroupInfo>{group.word_count} words</GroupInfo>
            </GroupCard>
          ))}
        </GroupsGrid>
        
        <StartButton 
          disabled={selectedGroupIds.size === 0}
          onClick={handleStartActivity}
        >
          Start {selectedActivity ? activities.find(a => a.id === selectedActivity)?.name : 'Activity'}
        </StartButton>
      </GroupsSection>
    </Container>
  );
};

export default ActivitySelector; 