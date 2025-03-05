import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import DashboardService, { 
  LastStudySession, 
  StudyProgress, 
  QuickStats 
} from '../../api/dashboardService';

import LastStudySessionCard from './LastStudySessionCard';
import StudyProgressCard from './StudyProgressCard';
import QuickStatsCard from './QuickStatsCard';
import StartStudyButton from './StartStudyButton';

const PageContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: ${theme.spacing.xl};
`;

const WelcomeHeader = styled.header`
  margin-bottom: ${theme.spacing.xxl};
`;

const Greeting = styled.h1`
  font-size: 2.2rem;
  color: ${theme.colors.textDark};
  margin-bottom: ${theme.spacing.sm};
`;

const Subtitle = styled.p`
  font-size: 1.1rem;
  color: ${theme.colors.textLight};
`;

const DashboardGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: ${theme.spacing.xl};
  
  @media (max-width: 992px) {
    grid-template-columns: 1fr;
  }
`;

const DashboardItem = styled.div`
  height: 100%;
`;

// Extends to two columns
const WideItem = styled(DashboardItem)`
  grid-column: span 2;
  
  @media (max-width: 992px) {
    grid-column: span 1;
  }
`;

const DashboardPage: React.FC = () => {
  const [lastSession, setLastSession] = useState<LastStudySession | null>(null);
  const [lastSessionLoading, setLastSessionLoading] = useState<boolean>(true);
  const [lastSessionError, setLastSessionError] = useState<Error | null>(null);
  
  const [progress, setProgress] = useState<StudyProgress | null>(null);
  const [progressLoading, setProgressLoading] = useState<boolean>(true);
  const [progressError, setProgressError] = useState<Error | null>(null);
  
  const [stats, setStats] = useState<QuickStats | null>(null);
  const [statsLoading, setStatsLoading] = useState<boolean>(true);
  const [statsError, setStatsError] = useState<Error | null>(null);
  
  // Get the user's name - would normally come from a user context or authentication service
  const username = "Student";
  
  // Get the greeting based on the time of day
  const getGreeting = (): string => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  };
  
  // Set document title with useEffect
  useEffect(() => {
    document.title = "Dashboard | Language Learning Portal";
    
    // Clean up when component unmounts
    return () => {
      document.title = "Language Learning Portal";
    };
  }, []);
  
  useEffect(() => {
    const fetchLastSession = async () => {
      try {
        setLastSessionLoading(true);
        const data = await DashboardService.getLastStudySession();
        setLastSession(data);
      } catch (error) {
        setLastSessionError(error as Error);
      } finally {
        setLastSessionLoading(false);
      }
    };
    
    const fetchProgress = async () => {
      try {
        setProgressLoading(true);
        const data = await DashboardService.getStudyProgress();
        setProgress(data);
      } catch (error) {
        setProgressError(error as Error);
      } finally {
        setProgressLoading(false);
      }
    };
    
    const fetchStats = async () => {
      try {
        setStatsLoading(true);
        const data = await DashboardService.getQuickStats();
        setStats(data);
      } catch (error) {
        setStatsError(error as Error);
      } finally {
        setStatsLoading(false);
      }
    };
    
    fetchLastSession();
    fetchProgress();
    fetchStats();
  }, []);
  
  return (
    <PageContainer>
      <WelcomeHeader>
        <Greeting>{getGreeting()}, {username}!</Greeting>
        <Subtitle>Welcome to your language learning dashboard. Track your progress and continue your studies.</Subtitle>
      </WelcomeHeader>
      
      <DashboardGrid>
        <DashboardItem>
          <LastStudySessionCard 
            session={lastSession} 
            loading={lastSessionLoading} 
            error={lastSessionError} 
          />
        </DashboardItem>
        
        <DashboardItem>
          <StartStudyButton />
        </DashboardItem>
        
        <WideItem>
          <StudyProgressCard 
            progress={progress} 
            loading={progressLoading} 
            error={progressError} 
          />
        </WideItem>
        
        <WideItem>
          <QuickStatsCard 
            stats={stats} 
            loading={statsLoading} 
            error={statsError} 
          />
        </WideItem>
      </DashboardGrid>
    </PageContainer>
  );
};

export default DashboardPage; 