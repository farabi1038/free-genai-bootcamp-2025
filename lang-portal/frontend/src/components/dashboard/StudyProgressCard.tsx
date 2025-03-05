import React from 'react';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import { StudyProgress } from '../../api/types';
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

const ProgressContent = styled.div`
  flex: 1;
`;

const ProgressSection = styled.div`
  margin-bottom: ${theme.spacing.xl};
`;

const ProgressTitle = styled.h3`
  font-size: 1.1rem;
  margin: 0 0 ${theme.spacing.md} 0;
  color: ${theme.colors.textDark};
`;

const ProgressBar = styled.div`
  background-color: ${theme.colors.snow1};
  height: 12px;
  border-radius: 6px;
  margin-bottom: ${theme.spacing.sm};
  overflow: hidden;
`;

const ProgressBarFill = styled.div<{ percentage: number; color: string }>`
  width: ${props => props.percentage}%;
  height: 100%;
  background-color: ${props => props.color};
  transition: width 0.5s ease;
`;

const ProgressStats = styled.div`
  display: flex;
  justify-content: space-between;
  color: ${theme.colors.textLight};
  font-size: 0.9rem;
`;

const ProgressStat = styled.div``;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${theme.spacing.md};
`;

const StatItem = styled.div`
  background-color: ${theme.colors.snow1};
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
`;

const StatValue = styled.div`
  font-size: 1.8rem;
  font-weight: bold;
  color: ${theme.colors.frost3};
`;

const StatLabel = styled.div`
  font-size: 0.9rem;
  color: ${theme.colors.textLight};
`;

const formatTime = (minutes: number): string => {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  
  if (hours === 0) {
    return `${mins} minutes`;
  }
  
  return `${hours}h ${mins}m`;
};

interface StudyProgressCardProps {
  progress: StudyProgress | null;
  loading: boolean;
  error: Error | null;
}

const StudyProgressCard: React.FC<StudyProgressCardProps> = ({ progress, loading, error }) => {
  if (loading) {
    return (
      <CardContainer>
        <CardHeader>
          <CardTitle><CardIcon>📊</CardIcon> Study Progress</CardTitle>
        </CardHeader>
        <LoadingIndicator text="Loading progress data..." />
      </CardContainer>
    );
  }
  
  if (error) {
    return (
      <CardContainer>
        <CardHeader>
          <CardTitle><CardIcon>📊</CardIcon> Study Progress</CardTitle>
        </CardHeader>
        <div>Error loading progress data. Please try again later.</div>
      </CardContainer>
    );
  }
  
  if (!progress) {
    return (
      <CardContainer>
        <CardHeader>
          <CardTitle><CardIcon>📊</CardIcon> Study Progress</CardTitle>
        </CardHeader>
        <div>No progress data available.</div>
      </CardContainer>
    );
  }
  
  const masteryPercentage = progress.masteryRate;
  const studiedPercentage = (progress.wordsStudied / progress.totalWords) * 100;
  
  return (
    <CardContainer>
      <CardHeader>
        <CardTitle><CardIcon>📊</CardIcon> Study Progress</CardTitle>
      </CardHeader>
      <ProgressContent>
        <ProgressSection>
          <ProgressTitle>Words Studied</ProgressTitle>
          <ProgressBar>
            <ProgressBarFill percentage={studiedPercentage} color={theme.colors.aurora4} />
          </ProgressBar>
          <ProgressStats>
            <ProgressStat>Studied: {progress.wordsStudied}</ProgressStat>
            <ProgressStat>Total: {progress.totalWords}</ProgressStat>
          </ProgressStats>
        </ProgressSection>
        
        <ProgressSection>
          <ProgressTitle>Mastery Rate</ProgressTitle>
          <ProgressBar>
            <ProgressBarFill percentage={masteryPercentage} color={theme.colors.frost3} />
          </ProgressBar>
          <ProgressStats>
            <ProgressStat>{masteryPercentage}% Mastered</ProgressStat>
          </ProgressStats>
        </ProgressSection>
      </ProgressContent>
    </CardContainer>
  );
};

export default StudyProgressCard; 