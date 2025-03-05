import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import { Group } from '../../api/types';

const Card = styled.div`
  background-color: ${theme.colors.card};
  border-radius: ${theme.borderRadius.md};
  box-shadow: ${theme.shadows.md};
  padding: ${theme.spacing.lg};
  display: flex;
  flex-direction: column;
  border: 1px solid ${theme.colors.border};
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
  height: 100%;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: ${theme.shadows.lg};
    cursor: pointer;
  }
`;

const GroupName = styled.h3`
  margin: 0 0 ${theme.spacing.md} 0;
  color: ${theme.colors.polar1};
  font-size: 1.3rem;
`;

const WordCount = styled.div`
  margin-top: auto;
  display: flex;
  align-items: center;
  color: ${theme.colors.textLight};
  font-size: 0.9rem;
  
  svg {
    margin-right: ${theme.spacing.xs};
  }
`;

interface GroupCardProps {
  group: Group;
}

const GroupCard: React.FC<GroupCardProps> = ({ group }) => {
  const navigate = useNavigate();
  
  const handleClick = () => {
    navigate(`/groups/${group.id}`);
  };
  
  return (
    <Card onClick={handleClick}>
      <GroupName>{group.name}</GroupName>
      <WordCount>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path>
          <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path>
        </svg>
        {group.word_count} {group.word_count === 1 ? 'word' : 'words'}
      </WordCount>
    </Card>
  );
};

export default GroupCard; 