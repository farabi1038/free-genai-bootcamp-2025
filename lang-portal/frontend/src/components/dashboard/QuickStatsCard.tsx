import React from 'react';
import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { theme } from '../../styles/theme';
import { QuickStats } from '../../api/types';
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

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${theme.spacing.lg};
  flex: 1;
`;

const StatItem = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: ${theme.colors.snow1};
  padding: ${theme.spacing.lg};
  border-radius: ${theme.borderRadius};
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
`;

const StatIcon = styled.div`
  font-size: 1.8rem;
  margin-bottom: ${theme.spacing.sm};
  color: ${theme.colors.frost2};
`;

const StatValue = styled.div`
  font-size: 1.8rem;
  font-weight: bold;
  color: ${theme.colors.textDark};
`;

const StatLabel = styled.div`
  font-size: 0.9rem;
  color: ${theme.colors.textLight};
  margin-top: ${theme.spacing.xs};
`;

const LinkStatItem = styled(Link)`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: ${theme.colors.snow1};
  padding: ${theme.spacing.lg};
  border-radius: ${theme.borderRadius};
  text-align: center;
  text-decoration: none;
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
`;

interface QuickStatsCardProps {
  stats: QuickStats | null;
  loading: boolean;
  error: Error | null;
}

const QuickStatsCard: React.FC<QuickStatsCardProps> = ({ stats, loading, error }) => {
  if (loading) {
    return (
      <CardContainer>
        <CardHeader>
          <CardTitle><CardIcon>🔍</CardIcon> Quick Stats</CardTitle>
        </CardHeader>
        <LoadingIndicator text="Loading stats..." />
      </CardContainer>
    );
  }
  
  if (error) {
    return (
      <CardContainer>
        <CardHeader>
          <CardTitle><CardIcon>🔍</CardIcon> Quick Stats</CardTitle>
        </CardHeader>
        <div>Error loading stats data. Please try again later.</div>
      </CardContainer>
    );
  }
  
  if (!stats) {
    return (
      <CardContainer>
        <CardHeader>
          <CardTitle><CardIcon>🔍</CardIcon> Quick Stats</CardTitle>
        </CardHeader>
        <div>No stats data available.</div>
      </CardContainer>
    );
  }
  
  return (
    <CardContainer>
      <CardHeader>
        <CardTitle><CardIcon>🔍</CardIcon> Quick Stats</CardTitle>
      </CardHeader>
      <StatsGrid>
        <LinkStatItem to="/sessions">
          <StatIcon>📚</StatIcon>
          <StatValue>{stats.totalSessions}</StatValue>
          <StatLabel>Total Sessions</StatLabel>
        </LinkStatItem>
        
        <LinkStatItem to="/groups">
          <StatIcon>📂</StatIcon>
          <StatValue>{stats.activeGroups}</StatValue>
          <StatLabel>Active Groups</StatLabel>
        </LinkStatItem>
        
        <StatItem>
          <StatIcon>🔥</StatIcon>
          <StatValue>{stats.streak}</StatValue>
          <StatLabel>Day Streak</StatLabel>
        </StatItem>
        
        <StatItem>
          <StatIcon>✓</StatIcon>
          <StatValue>{stats.successRate}%</StatValue>
          <StatLabel>Success Rate</StatLabel>
        </StatItem>
      </StatsGrid>
    </CardContainer>
  );
};

export default QuickStatsCard; 