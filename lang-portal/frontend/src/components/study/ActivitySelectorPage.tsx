import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import activitiesService from '../../api/activitiesService';
import { ActivityType } from '../../api/types';
import LoadingIndicator from '../ui/LoadingIndicator';
import { useSettings } from '../../contexts/SettingsContext';
import groupService from '../../api/groupService';

const Container = styled.div`
  padding: ${theme.spacing.lg};
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  margin-bottom: ${theme.spacing.lg};
`;

const Title = styled.h1`
  color: ${theme.colors.textDark};
  margin: 0 0 ${theme.spacing.sm} 0;
`;

const Description = styled.p`
  color: ${theme.colors.textLight};
  margin: 0;
`;

const ActivityGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: ${theme.spacing.lg};
  margin-bottom: ${theme.spacing.xl};
`;

const ActivityCard = styled.div<{ selected: boolean }>`
  background-color: ${props => props.selected ? theme.colors.frost0 : theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.lg};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, background-color 0.2s;
  border: 2px solid ${props => props.selected ? theme.colors.frost3 : 'transparent'};
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
`;

const ActivityIcon = styled.div`
  font-size: 2rem;
  color: ${theme.colors.frost3};
  margin-bottom: ${theme.spacing.md};
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  width: 60px;
  background-color: ${theme.colors.snow1};
  border-radius: 50%;
`;

const ActivityName = styled.h2`
  color: ${theme.colors.textDark};
  margin: 0 0 ${theme.spacing.sm} 0;
`;

const ActivityDescription = styled.p`
  color: ${theme.colors.textLight};
  margin: 0 0 ${theme.spacing.sm} 0;
  font-size: 0.9rem;
`;

const DifficultyBadge = styled.span<{ difficulty: 'beginner' | 'intermediate' | 'advanced' }>`
  display: inline-block;
  padding: ${theme.spacing.xs} ${theme.spacing.sm};
  border-radius: ${theme.borderRadius};
  font-size: 0.8rem;
  background-color: ${props => {
    switch (props.difficulty) {
      case 'beginner': return 'rgba(163, 190, 140, 0.2)';
      case 'intermediate': return 'rgba(235, 203, 139, 0.2)';
      case 'advanced': return 'rgba(191, 97, 106, 0.2)';
      default: return 'rgba(163, 190, 140, 0.2)';
    }
  }};
  color: ${props => {
    switch (props.difficulty) {
      case 'beginner': return theme.colors.aurora4;
      case 'intermediate': return theme.colors.aurora3;
      case 'advanced': return theme.colors.aurora0;
      default: return theme.colors.aurora4;
    }
  }};
  margin-top: ${theme.spacing.sm};
`;

const DetailsSection = styled.div`
  margin-bottom: ${theme.spacing.xl};
`;

const DetailCard = styled.div`
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.lg};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const SectionTitle = styled.h2`
  color: ${theme.colors.textDark};
  margin: 0 0 ${theme.spacing.md} 0;
  font-size: 1.5rem;
`;

const BenefitsList = styled.ul`
  margin: ${theme.spacing.md} 0;
  padding-left: 20px;
  
  li {
    margin-bottom: ${theme.spacing.sm};
    color: ${theme.colors.textDark};
  }
`;

const InstructionsBox = styled.div`
  background-color: ${theme.colors.frost0};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.md};
  margin: ${theme.spacing.md} 0;
  border-left: 4px solid ${theme.colors.frost2};
`;

const StartButtonContainer = styled.div`
  display: flex;
  justify-content: center;
  margin-top: ${theme.spacing.lg};
`;

const StartButton = styled.button`
  background-color: ${theme.colors.frost3};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.md} ${theme.spacing.xl};
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: ${theme.colors.frost2};
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

const GroupSelection = styled.div`
  margin-top: ${theme.spacing.lg};
`;

const GroupSelect = styled.select`
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  border: 1px solid ${theme.colors.snow3};
  background-color: white;
  width: 100%;
  max-width: 400px;
  margin-top: ${theme.spacing.sm};
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.frost2};
    box-shadow: 0 0 0 2px rgba(94, 129, 172, 0.2);
  }
`;

const Label = styled.label`
  font-weight: bold;
  color: ${theme.colors.textDark};
  margin-bottom: ${theme.spacing.xs};
  display: block;
`;

const ActivitySelectorPage: React.FC = () => {
  const navigate = useNavigate();
  const { settings } = useSettings();
  const [activities, setActivities] = useState<ActivityType[]>([]);
  const [selectedActivity, setSelectedActivity] = useState<ActivityType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [groups, setGroups] = useState<{id: string, name: string}[]>([]);
  const [selectedGroupId, setSelectedGroupId] = useState<string>('');
  
  useEffect(() => {
    const fetchActivities = async () => {
      try {
        setLoading(true);
        const data = await activitiesService.getAllActivities();
        setActivities(data);
        
        // If there's a default activity in settings, select it
        if (settings?.defaultStudyActivity) {
          const defaultActivity = data.find(a => a.id === settings.defaultStudyActivity);
          if (defaultActivity) {
            setSelectedActivity(defaultActivity);
          }
        } else if (data.length > 0) {
          // Otherwise select the first activity
          setSelectedActivity(data[0]);
        }
        
        setError(null);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchActivities();
  }, [settings]);
  
  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const data = await groupService.getAllGroups();
        setGroups(data.map(group => ({
          id: group.id,
          name: group.name
        })));
      } catch (err) {
        console.error("Error fetching groups:", err);
      }
    };
    
    fetchGroups();
  }, []);
  
  const handleSelectActivity = (activity: ActivityType) => {
    setSelectedActivity(activity);
  };
  
  const handleStartActivity = () => {
    if (selectedActivity && selectedGroupId) {
      navigate(`/study/${selectedActivity.id}?groupId=${selectedGroupId}`);
    }
  };
  
  if (loading && activities.length === 0) {
    return (
      <Container>
        <LoadingIndicator text="Loading study activities..." />
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container>
        <ErrorMessage>
          Error loading study activities: {error.message}
        </ErrorMessage>
      </Container>
    );
  }
  
  // Map activity icon names to emoji for simplicity
  const getIconForActivity = (iconName: string) => {
    switch (iconName) {
      case 'card': return '🃏';
      case 'list': return '📝';
      case 'keyboard': return '⌨️';
      case 'grid': return '🎮';
      default: return '📚';
    }
  };
  
  return (
    <Container>
      <Header>
        <Title>Study Activities</Title>
        <Description>Choose an activity to practice your vocabulary</Description>
      </Header>
      
      <ActivityGrid>
        {activities.map(activity => (
          <ActivityCard 
            key={activity.id}
            selected={selectedActivity?.id === activity.id}
            onClick={() => handleSelectActivity(activity)}
          >
            <ActivityIcon>{getIconForActivity(activity.icon)}</ActivityIcon>
            <ActivityName>{activity.name}</ActivityName>
            <ActivityDescription>{activity.description}</ActivityDescription>
            <DifficultyBadge difficulty={activity.difficulty}>
              {activity.difficulty.charAt(0).toUpperCase() + activity.difficulty.slice(1)}
            </DifficultyBadge>
          </ActivityCard>
        ))}
      </ActivityGrid>
      
      {selectedActivity && (
        <DetailsSection>
          <SectionTitle>{selectedActivity.name}</SectionTitle>
          <DetailCard>
            <h3>Benefits</h3>
            <BenefitsList>
              {selectedActivity.benefits.map((benefit, index) => (
                <li key={index}>{benefit}</li>
              ))}
            </BenefitsList>
            
            <h3>Recommended For</h3>
            <p>{selectedActivity.recommendedFor}</p>
            
            <h3>How to Use</h3>
            <InstructionsBox>
              {selectedActivity.instructions}
            </InstructionsBox>
            
            <GroupSelection>
              <Label htmlFor="groupSelect">Select a Word Group to Study</Label>
              <GroupSelect 
                id="groupSelect"
                value={selectedGroupId}
                onChange={(e) => setSelectedGroupId(e.target.value)}
              >
                <option value="">-- Select a group --</option>
                {groups.map(group => (
                  <option key={group.id} value={group.id}>
                    {group.name}
                  </option>
                ))}
              </GroupSelect>
            </GroupSelection>
            
            <StartButtonContainer>
              <StartButton 
                onClick={handleStartActivity}
                disabled={!selectedGroupId}
              >
                Start {selectedActivity.name}
              </StartButton>
            </StartButtonContainer>
          </DetailCard>
        </DetailsSection>
      )}
    </Container>
  );
};

export default ActivitySelectorPage; 