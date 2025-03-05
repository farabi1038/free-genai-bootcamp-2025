import { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import styled from 'styled-components';
import useApi from '../hooks/useApi';
import DashboardService from '../api/dashboardService';
import { format } from 'date-fns';
import { theme } from '../styles/theme';
import LoadingIndicator from './ui/LoadingIndicator';

const DashboardContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: ${theme.spacing.lg};
`;

const Card = styled.div`
  background-color: ${theme.colors.card};
  padding: ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.md};
  box-shadow: ${theme.shadows.md};
  border: 1px solid ${theme.colors.border};
`;

const CardTitle = styled.h3`
  margin-top: 0;
  margin-bottom: ${theme.spacing.md};
  border-bottom: 1px solid ${theme.colors.border};
  padding-bottom: ${theme.spacing.sm};
  color: ${theme.colors.primary};
  font-weight: 600;
`;

const StudyButton = styled.button`
  background-color: ${theme.colors.secondary};
  color: ${theme.colors.snow3};
  border: none;
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  border-radius: ${theme.borderRadius.sm};
  font-size: 16px;
  cursor: pointer;
  margin-top: ${theme.spacing.lg};
  width: 100%;
  font-weight: 500;
  
  &:hover {
    background-color: #8CAA7A; /* Slightly darker green */
  }
`;

const StatGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: ${theme.spacing.sm};
`;

const StatItem = styled.div`
  background-color: ${theme.colors.background};
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius.sm};
  text-align: center;
  border: 1px solid ${theme.colors.border};
`;

const StatValue = styled.div`
  font-size: 24px;
  font-weight: bold;
  color: ${theme.colors.primary};
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: ${theme.colors.textLight};
  margin-top: ${theme.spacing.xs};
`;

const ErrorMessage = styled.div`
  color: ${theme.colors.aurora1};
  background-color: #FFF0F0;
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius.sm};
  margin-bottom: ${theme.spacing.lg};
  border: 1px solid #FFDCDC;
`;

const GroupLink = styled(Link)`
  color: ${theme.colors.frost4};
  font-weight: 500;
  text-decoration: none;
  &:hover {
    text-decoration: underline;
  }
`;

const PageHeading = styled.h1`
  color: ${theme.colors.polar1};
  margin-bottom: ${theme.spacing.lg};
  font-size: 2.2rem;
`;

const Dashboard = () => {
  const navigate = useNavigate();
  
  // API calls using the useApi hook
  const { 
    data: lastSession, 
    loading: loadingLastSession, 
    error: lastSessionError,
    execute: fetchLastSession 
  } = useApi(DashboardService.getLastStudySession);
  
  const { 
    data: progress, 
    loading: loadingProgress,
    error: progressError, 
    execute: fetchProgress 
  } = useApi(DashboardService.getStudyProgress);
  
  const { 
    data: quickStats, 
    loading: loadingStats,
    error: statsError, 
    execute: fetchStats 
  } = useApi(DashboardService.getQuickStats);
  
  // Fetch data on component mount
  useEffect(() => {
    fetchLastSession();
    fetchProgress();
    fetchStats();
  }, [fetchLastSession, fetchProgress, fetchStats]);
  
  // Navigate to study activities page
  const handleStartStudying = () => {
    navigate('/study');
  };
  
  // Overall loading state
  const isLoading = loadingLastSession || loadingProgress || loadingStats;
  
  // Combine all errors
  const error = lastSessionError || progressError || statsError;

  if (isLoading) {
    return <LoadingIndicator text="Loading dashboard data..." />;
  }

  if (error) {
    return <ErrorMessage>Error: {error.message}</ErrorMessage>;
  }

  return (
    <>
      <PageHeading>Dashboard</PageHeading>
      <DashboardContainer>
        <Card>
          <CardTitle>Last Study Session</CardTitle>
          {lastSession ? (
            <>
              <p>Activity: {lastSession.activity}</p>
              <p>Time: {format(new Date(lastSession.timestamp), 'PPp')}</p>
              <p>Results: {lastSession.correct} correct, {lastSession.wrong} wrong</p>
              <p>Group: <GroupLink to={`/groups/${lastSession.group_id}`}>{lastSession.group}</GroupLink></p>
            </>
          ) : (
            <p>No study sessions yet. Start studying to see your progress!</p>
          )}
        </Card>
        
        <Card>
          <CardTitle>Study Progress</CardTitle>
          {progress ? (
            <>
              <p>Words studied: {progress.wordsStudied}/{progress.totalWords}</p>
              <p>Mastery progress: {progress.masteryRate}%</p>
            </>
          ) : (
            <p>No progress data available.</p>
          )}
          <StudyButton onClick={handleStartStudying}>Start Studying</StudyButton>
        </Card>
        
        <Card>
          <CardTitle>Quick Stats</CardTitle>
          {quickStats ? (
            <StatGrid>
              <StatItem>
                <StatValue>{quickStats.successRate}%</StatValue>
                <StatLabel>Success Rate</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{quickStats.totalSessions}</StatValue>
                <StatLabel>Study Sessions</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{quickStats.activeGroups}</StatValue>
                <StatLabel>Active Groups</StatLabel>
              </StatItem>
              <StatItem>
                <StatValue>{quickStats.streak} days</StatValue>
                <StatLabel>Study Streak</StatLabel>
              </StatItem>
            </StatGrid>
          ) : (
            <p>No statistics available yet.</p>
          )}
        </Card>
      </DashboardContainer>
    </>
  );
};

export default Dashboard; 