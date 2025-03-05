import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { theme } from '../../../styles/theme';
import { Word, Group } from '../../../api/types';
import { shuffleArray } from '../../../utils/arrayUtils';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
`;

const Header = styled.div`
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing.xl};
`;

const Title = styled.h1`
  color: ${theme.colors.textDark};
  margin: 0;
`;

const StatsContainer = styled.div`
  text-align: right;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background-color: ${theme.colors.snow1};
  border-radius: 4px;
  margin: ${theme.spacing.md} 0;
  overflow: hidden;
`;

const Progress = styled.div<{ width: number }>`
  height: 100%;
  width: ${props => props.width}%;
  background-color: ${theme.colors.frost3};
  transition: width 0.3s ease;
`;

const Controls = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.xl};
`;

const Button = styled.button`
  background-color: ${theme.colors.frost2};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: ${theme.colors.frost3};
  }
  
  &:disabled {
    background-color: ${theme.colors.disabled};
    cursor: not-allowed;
  }
`;

const Card = styled.div`
  width: 500px;
  height: 300px;
  perspective: 1000px;
  margin-bottom: ${theme.spacing.xl};
  cursor: pointer;
`;

const CardInner = styled.div<{ flipped: boolean }>`
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
  transform: ${props => props.flipped ? 'rotateY(180deg)' : 'rotateY(0deg)'};
`;

const CardFace = styled.div`
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  border-radius: ${theme.borderRadius};
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: ${theme.spacing.lg};
`;

const CardFront = styled(CardFace)`
  background-color: ${theme.colors.polarNight1};
  color: ${theme.colors.snow0};
`;

const CardBack = styled(CardFace)`
  background-color: ${theme.colors.snow0};
  color: ${theme.colors.polarNight1};
  transform: rotateY(180deg);
`;

const JapaneseText = styled.h2`
  font-size: 2.5rem;
  margin-bottom: ${theme.spacing.md};
`;

const RomajiText = styled.p`
  font-size: 1.2rem;
  color: ${theme.colors.frost1};
  margin-bottom: ${theme.spacing.lg};
`;

const EnglishText = styled.h3`
  font-size: 1.8rem;
`;

const ButtonContainer = styled.div`
  display: flex;
  gap: ${theme.spacing.md};
  margin-top: ${theme.spacing.xl};
`;

const FeedbackButton = styled.button<{ correct?: boolean }>`
  background-color: ${props => props.correct ? theme.colors.success : theme.colors.error};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: ${props => props.correct ? theme.colors.aurora4 : theme.colors.aurora0};
  }
`;

const CompletionMessage = styled.div`
  text-align: center;
  padding: ${theme.spacing.xl};
`;

interface FlashcardsActivityProps {
  words: Word[];
  groups: Group[];
}

// Create a utility function for array shuffling if it doesn't exist
const shuffleArrayFunc = <T extends unknown>(array: T[]): T[] => {
  const newArray = [...array];
  for (let i = newArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
  }
  return newArray;
};

const FlashcardsActivity: React.FC<FlashcardsActivityProps> = ({ words, groups }) => {
  const [direction, setDirection] = useState<'ja-en' | 'en-ja'>('ja-en');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [studyWords, setStudyWords] = useState<Word[]>([]);
  const [completed, setCompleted] = useState(false);
  const [correctCount, setCorrectCount] = useState(0);
  const [incorrectCount, setIncorrectCount] = useState(0);
  
  // Shuffle the words on mount or when the direction changes
  useEffect(() => {
    const shuffleFunc = typeof shuffleArray === 'function' ? shuffleArray : shuffleArrayFunc;
    setStudyWords(shuffleFunc([...words]));
    setCurrentIndex(0);
    setFlipped(false);
    setCompleted(false);
    setCorrectCount(0);
    setIncorrectCount(0);
  }, [words, direction]);
  
  const currentWord = studyWords[currentIndex];
  const progress = (currentIndex / studyWords.length) * 100;
  
  const handleFlip = () => {
    setFlipped(!flipped);
  };
  
  const handleNext = () => {
    if (currentIndex < studyWords.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setFlipped(false);
    } else {
      setCompleted(true);
    }
  };
  
  const handleFeedback = (correct: boolean) => {
    if (correct) {
      setCorrectCount(correctCount + 1);
    } else {
      setIncorrectCount(incorrectCount + 1);
    }
    handleNext();
  };
  
  const restartActivity = () => {
    const shuffleFunc = typeof shuffleArray === 'function' ? shuffleArray : shuffleArrayFunc;
    setStudyWords(shuffleFunc([...words]));
    setCurrentIndex(0);
    setFlipped(false);
    setCompleted(false);
    setCorrectCount(0);
    setIncorrectCount(0);
  };
  
  if (completed) {
    return (
      <Container>
        <CompletionMessage>
          <h2>Study Session Complete!</h2>
          <p>You've reviewed all {studyWords.length} words.</p>
          <p>Correct: {correctCount} | Incorrect: {incorrectCount}</p>
          
          <Button onClick={restartActivity} style={{ marginTop: theme.spacing.lg }}>
            Start Again
          </Button>
        </CompletionMessage>
      </Container>
    );
  }
  
  if (!currentWord) {
    return <div>No words to study</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>Flashcards</Title>
        <StatsContainer>
          <p>Studying {studyWords.length} words from {groups.length} groups</p>
          <p>Card {currentIndex + 1} of {studyWords.length}</p>
        </StatsContainer>
      </Header>
      
      <Controls>
        <Button 
          onClick={() => setDirection('ja-en')}
          disabled={direction === 'ja-en'}
        >
          Japanese → English
        </Button>
        <Button 
          onClick={() => setDirection('en-ja')}
          disabled={direction === 'en-ja'}
        >
          English → Japanese
        </Button>
      </Controls>
      
      <ProgressBar>
        <Progress width={progress} />
      </ProgressBar>
      
      <Card onClick={handleFlip}>
        <CardInner flipped={flipped}>
          <CardFront>
            {direction === 'ja-en' ? (
              <>
                <JapaneseText>{currentWord.japanese}</JapaneseText>
                <RomajiText>{currentWord.romaji}</RomajiText>
              </>
            ) : (
              <EnglishText>{currentWord.english}</EnglishText>
            )}
          </CardFront>
          <CardBack>
            {direction === 'ja-en' ? (
              <EnglishText>{currentWord.english}</EnglishText>
            ) : (
              <>
                <JapaneseText>{currentWord.japanese}</JapaneseText>
                <RomajiText>{currentWord.romaji}</RomajiText>
              </>
            )}
            <ButtonContainer>
              <FeedbackButton 
                onClick={(e) => {
                  e.stopPropagation();
                  handleFeedback(false);
                }}
              >
                Got it Wrong
              </FeedbackButton>
              <FeedbackButton 
                correct 
                onClick={(e) => {
                  e.stopPropagation();
                  handleFeedback(true);
                }}
              >
                Got it Right
              </FeedbackButton>
            </ButtonContainer>
          </CardBack>
        </CardInner>
      </Card>
      
      <Button onClick={handleNext}>
        Skip
      </Button>
    </Container>
  );
};

export default FlashcardsActivity; 