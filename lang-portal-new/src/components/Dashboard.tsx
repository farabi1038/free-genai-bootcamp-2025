import styled from 'styled-components';

const DashboardContainer = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
`;

const Card = styled.div`
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const CardTitle = styled.h3`
  margin-top: 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  color: #333;
`;

const StudyButton = styled.button`
  background-color: #4CAF50;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 20px;
  width: 100%;
  &:hover {
    background-color: #45a049;
  }
`;

const StatGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
`;

const StatItem = styled.div`
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 24px;
  font-weight: bold;
  color: #333;
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: #666;
  margin-top: 5px;
`;

const Dashboard = () => {
  // Mock data for testing
  const lastSession = {
    activity: 'Vocabulary Quiz',
    timestamp: '2025-03-05T09:30:00',
    correct: 15,
    wrong: 3,
    group: 'Basic Japanese'
  };

  const progress = {
    wordsStudied: 3,
    totalWords: 124,
    masteryRate: 0
  };

  const quickStats = {
    successRate: 80,
    totalSessions: 4,
    activeGroups: 3,
    streak: 4
  };

  return (
    <>
      <h1>Dashboard</h1>
      <DashboardContainer>
        <Card>
          <CardTitle>Last Study Session</CardTitle>
          <p>Activity: {lastSession.activity}</p>
          <p>Time: {new Date(lastSession.timestamp).toLocaleString()}</p>
          <p>Results: {lastSession.correct} correct, {lastSession.wrong} wrong</p>
          <p>Group: {lastSession.group}</p>
        </Card>
        
        <Card>
          <CardTitle>Study Progress</CardTitle>
          <p>Words studied: {progress.wordsStudied}/{progress.totalWords}</p>
          <p>Mastery progress: {progress.masteryRate}%</p>
          <StudyButton>Start Studying</StudyButton>
        </Card>
        
        <Card>
          <CardTitle>Quick Stats</CardTitle>
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
        </Card>
      </DashboardContainer>
    </>
  );
};

export default Dashboard; 