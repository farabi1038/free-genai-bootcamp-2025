import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { theme } from '../../../styles/theme';
import { Word } from '../../../api/types';
import { useNavigate } from 'react-router-dom';
import LoadingIndicator from '../../ui/LoadingIndicator';
import { useSettings } from '../../../contexts/SettingsContext';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 800px;
  margin: 0 auto;
`;

const FlashcardContainer = styled.div`
  width: 100%;
  perspective: 1000px;
  margin-bottom: ${theme.spacing.lg};
`;

const Flashcard = styled.div<{ flipped: boolean }>`
  width: 100%;
  height: 300px;
  position: relative;
  transition: transform 0.6s;
  transform-style: preserve-3d;
  transform: ${props => props.flipped ? 'rotateY(180deg)' : 'rotateY(0deg)'};
  cursor: pointer;
`;

const CardFace = styled.div`
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: ${theme.borderRadius};
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: ${theme.spacing.lg};
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const CardFront = styled(CardFace)`
  background-color: ${theme.colors.snow0};
  color: ${theme.colors.textDark};
`;

const CardBack = styled(CardFace)`
  background-color: ${theme.colors.frost0};
  color: ${theme.colors.textDark};
  transform: rotateY(180deg);
`;

const JapaneseText = styled.h1`
  font-size: 2.5rem;
  margin-bottom: ${theme.spacing.md};
  text-align: center;
`;

const RomajiText = styled.p`
  font-size: 1.2rem;
  color: ${theme.colors.textLight};
  margin-bottom: ${theme.spacing.lg};
  text-align: center;
`;

const EnglishText = styled.h2`
  font-size: 1.8rem;
  margin-bottom: ${theme.spacing.md};
  text-align: center;
`;

const ControlsContainer = styled.div`
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-top: ${theme.spacing.xl};
`;

const ControlButton = styled.button`
  background-color: ${theme.colors.snow0};
  border: none;
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  
  &:hover {
    background-color: ${theme.colors.snow1};
  }
  
  &:disabled {
    background-color: ${theme.colors.disabled};
    cursor: not-allowed;
  }
`;

const IncorrectButton = styled(ControlButton)`
  color: ${theme.colors.aurora0};
  border-left: 4px solid ${theme.colors.aurora0};
`;

const CorrectButton = styled(ControlButton)`
  color: ${theme.colors.aurora4};
  border-left: 4px solid ${theme.colors.aurora4};
`;

const ProgressContainer = styled.div`
  width: 100%;
  margin-bottom: ${theme.spacing.lg};
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background-color: ${theme.colors.snow1};
  border-radius: 4px;
  overflow: hidden;
`;

const ProgressFill = styled.div<{ width: number }>`
  height: 100%;
  width: ${props => props.width}%;
  background-color: ${theme.colors.frost3};
  transition: width 0.3s ease;
`;

const ProgressText = styled.div`
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: ${theme.colors.textLight};
  margin-top: ${theme.spacing.xs};
`;

const CompletionCard = styled.div`
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.xl};
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  width: 100%;
`;

const CompletionTitle = styled.h2`
  color: ${theme.colors.textDark};
  margin-bottom: ${theme.spacing.lg};
`;

const StatsContainer = styled.div`
  display: flex;
  justify-content: center;
  gap: ${theme.spacing.xl};
  margin-bottom: ${theme.spacing.xl};
`;

const StatCard = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const StatValue = styled.div<{ isCorrect?: boolean }>`
  font-size: 2rem;
  font-weight: bold;
  color: ${props => props.isCorrect ? theme.colors.aurora4 : theme.colors.aurora0};
  margin-bottom: ${theme.spacing.xs};
`;

const StatLabel = styled.div`
  font-size: 0.9rem;
  color: ${theme.colors.textLight};
`;

const ActionButton = styled.button`
  background-color: ${theme.colors.frost3};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
  margin: 0 ${theme.spacing.md};
  
  &:hover {
    background-color: ${theme.colors.frost2};
  }
`;

const CardHint = styled.div`
  color: ${theme.colors.textLight};
  font-size: 0.9rem;
  margin-top: ${theme.spacing.lg};
  font-style: italic;
`;

const ErrorMessage = styled.div`
  color: ${theme.colors.aurora0};
  font-size: 1.2rem;
  margin-bottom: ${theme.spacing.lg};
`;

const BackButton = styled.button`
  background-color: ${theme.colors.frost3};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: ${theme.colors.frost2};
  }
`;

const FlashcardActivity: React.FC<{ words: Word[]; groupId: string }> = ({ words, groupId }) => {
  const [wordsToStudy, setWordsToStudy] = useState<Word[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [correctCount, setCorrectCount] = useState(0);
  const [wrongCount, setWrongCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  
  useEffect(() => {
    if (words && words.length > 0) {
      console.log("Preparing flashcards with", words.length, "words");
      const shuffled = [...words].sort(() => 0.5 - Math.random());
      const limitedWords = shuffled.slice(0, Math.min(20, shuffled.length));
      setWordsToStudy(limitedWords);
      setLoading(false);
    } else {
      console.error("No words available for flashcards");
      setLoading(false);
    }
  }, [words]);
  
  const handleFlip = () => {
    setFlipped(!flipped);
  };
  
  const handleResponse = (isCorrect: boolean) => {
    if (isCorrect) {
      setCorrectCount(prev => prev + 1);
    } else {
      setWrongCount(prev => prev + 1);
    }
    
    // Move to next card
    if (currentIndex < wordsToStudy.length - 1) {
      setCurrentIndex(prev => prev + 1);
      setFlipped(false);
    } else {
      setCompleted(true);
    }
  };
  
  const handleReturnToActivities = () => {
    navigate('/study');
  };
  
  const handleStudyAgain = () => {
    // Reset state and shuffle words again
    setCurrentIndex(0);
    setFlipped(false);
    setCompleted(false);
    setCorrectCount(0);
    setWrongCount(0);
    
    if (words && words.length > 0) {
      const shuffled = [...words].sort(() => 0.5 - Math.random());
      const limitedWords = shuffled.slice(0, Math.min(20, shuffled.length));
      setWordsToStudy(limitedWords);
    }
  };
  
  if (loading) {
    return <LoadingIndicator text="Preparing flashcards..." />;
  }
  
  if (!wordsToStudy || wordsToStudy.length === 0) {
    return (
      <Container>
        <ErrorMessage>
          No words available for this group. Please select a different group.
        </ErrorMessage>
        <BackButton onClick={() => navigate('/study')}>
          Back to Activities
        </BackButton>
      </Container>
    );
  }
  
  if (completed) {
    return (
      <Container>
        <CompletionCard>
          <CompletionTitle>Study Session Complete!</CompletionTitle>
          <StatsContainer>
            <StatCard>
              <StatValue isCorrect={true}>{correctCount}</StatValue>
              <StatLabel>Correct</StatLabel>
            </StatCard>
            <StatCard>
              <StatValue isCorrect={false}>{wrongCount}</StatValue>
              <StatLabel>Incorrect</StatLabel>
            </StatCard>
            <StatCard>
              <StatValue>{wordsToStudy.length}</StatValue>
              <StatLabel>Total Words</StatLabel>
            </StatCard>
          </StatsContainer>
          <div>
            <ActionButton onClick={handleStudyAgain}>Study Again</ActionButton>
            <ActionButton onClick={handleReturnToActivities}>Return to Activities</ActionButton>
          </div>
        </CompletionCard>
      </Container>
    );
  }
  
  const currentWord = wordsToStudy[currentIndex];
  const progress = ((currentIndex + 1) / wordsToStudy.length) * 100;
  
  return (
    <Container>
      <ProgressContainer>
        <ProgressBar>
          <ProgressFill width={progress} />
        </ProgressBar>
        <ProgressText>
          <span>Word {currentIndex + 1} of {wordsToStudy.length}</span>
          <span>{Math.round(progress)}% Complete</span>
        </ProgressText>
      </ProgressContainer>
      
      <FlashcardContainer>
        <Flashcard flipped={flipped} onClick={handleFlip}>
          <CardFront>
            <JapaneseText>{currentWord.japanese}</JapaneseText>
            <RomajiText>{currentWord.romaji}</RomajiText>
            <CardHint>Click the card to reveal the translation</CardHint>
          </CardFront>
          <CardBack>
            <EnglishText>{currentWord.english}</EnglishText>
          </CardBack>
        </Flashcard>
      </FlashcardContainer>
      
      <ControlsContainer>
        <IncorrectButton onClick={() => handleResponse(false)}>
          I Don't Know
        </IncorrectButton>
        <CorrectButton onClick={() => handleResponse(true)}>
          I Know This
        </CorrectButton>
      </ControlsContainer>
    </Container>
  );
};

export default FlashcardActivity; 