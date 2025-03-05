import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import wordService from '../../api/wordService';
import { Word } from '../../api/types';
import LoadingIndicator from '../ui/LoadingIndicator';

const Container = styled.div`
  padding: ${theme.spacing.lg};
  max-width: 800px;
  margin: 0 auto;
`;

const Card = styled.div`
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.xl};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const Header = styled.div`
  margin-bottom: ${theme.spacing.xl};
  border-bottom: 1px solid ${theme.colors.snow1};
  padding-bottom: ${theme.spacing.lg};
`;

const Title = styled.h1`
  color: ${theme.colors.textDark};
  margin: 0 0 ${theme.spacing.md} 0;
  font-size: 2.5rem;
`;

const Pronunciation = styled.h2`
  color: ${theme.colors.textLight};
  font-weight: normal;
  margin: 0 0 ${theme.spacing.md} 0;
`;

const Translation = styled.h3`
  color: ${theme.colors.frost3};
  margin: 0;
  font-size: 1.5rem;
`;

const Section = styled.div`
  margin: ${theme.spacing.xl} 0;
`;

const SectionTitle = styled.h3`
  color: ${theme.colors.textDark};
  margin: 0 0 ${theme.spacing.md} 0;
  font-size: 1.2rem;
`;

const StatsContainer = styled.div`
  display: flex;
  gap: ${theme.spacing.xl};
`;

const StatBox = styled.div`
  background-color: ${theme.colors.frost1};
  color: white;
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  text-align: center;
  flex: 1;
`;

const StatNumber = styled.div`
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: ${theme.spacing.xs};
`;

const StatLabel = styled.div`
  font-size: 0.9rem;
`;

const GroupsContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: ${theme.spacing.sm};
  margin-top: ${theme.spacing.md};
`;

const GroupTag = styled(Link)`
  background-color: ${theme.colors.frost2};
  color: white;
  padding: ${theme.spacing.xs} ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  text-decoration: none;
  font-size: 0.9rem;
  
  &:hover {
    background-color: ${theme.colors.frost3};
  }
`;

const BackLink = styled(Link)`
  display: inline-block;
  color: ${theme.colors.frost3};
  text-decoration: none;
  margin-top: ${theme.spacing.xl};
  
  &:hover {
    text-decoration: underline;
  }
`;

const ErrorMessage = styled.div`
  background-color: ${theme.colors.aurora0};
  color: white;
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  margin-bottom: ${theme.spacing.md};
`;

const WordDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [word, setWord] = useState<Word | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  
  useEffect(() => {
    const fetchWord = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        const data = await wordService.getWordById(id);
        setWord(data);
        setError(null);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchWord();
  }, [id]);
  
  if (loading) {
    return (
      <Container>
        <LoadingIndicator text="Loading word details..." />
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container>
        <ErrorMessage>
          Error loading word: {error.message}
        </ErrorMessage>
        <BackLink to="/words">&larr; Back to Words</BackLink>
      </Container>
    );
  }
  
  if (!word) {
    return (
      <Container>
        <ErrorMessage>
          Word not found
        </ErrorMessage>
        <BackLink to="/words">&larr; Back to Words</BackLink>
      </Container>
    );
  }
  
  return (
    <Container>
      <Card>
        <Header>
          <Title>{word.japanese}</Title>
          <Pronunciation>{word.romaji}</Pronunciation>
          <Translation>{word.english}</Translation>
        </Header>
        
        <Section>
          <SectionTitle>Study Statistics</SectionTitle>
          <StatsContainer>
            <StatBox>
              <StatNumber>{word.correct_count}</StatNumber>
              <StatLabel>Correct</StatLabel>
            </StatBox>
            <StatBox>
              <StatNumber>{word.wrong_count}</StatNumber>
              <StatLabel>Wrong</StatLabel>
            </StatBox>
            <StatBox>
              <StatNumber>{Math.round((word.correct_count / (word.correct_count + word.wrong_count || 1)) * 100)}%</StatNumber>
              <StatLabel>Success Rate</StatLabel>
            </StatBox>
          </StatsContainer>
        </Section>
        
        <Section>
          <SectionTitle>Word Groups</SectionTitle>
          <GroupsContainer>
            {word.groups && word.groups.length > 0 ? (
              word.groups.map(groupId => (
                <GroupTag key={groupId} to={`/groups/${groupId}`}>
                  {groupId.replace('group', 'Group ')}
                </GroupTag>
              ))
            ) : (
              <p>This word is not in any groups.</p>
            )}
          </GroupsContainer>
        </Section>
      </Card>
      
      <BackLink to="/words">&larr; Back to Words</BackLink>
    </Container>
  );
};

export default WordDetails; 