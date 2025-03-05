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

const QuestionCard = styled.div`
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.xl};
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  width: 100%;
  margin-bottom: ${theme.spacing.lg};
`;

const Question = styled.div`
  text-align: center;
  margin-bottom: ${theme.spacing.lg};
`;

const QuestionText = styled.h1`
  font-size: 2rem;
  color: ${theme.colors.textDark};
  margin-bottom: ${theme.spacing.sm};
`;

const RomajiText = styled.p`
  font-size: 1.2rem;
  color: ${theme.colors.textLight};
`;

const ChoicesContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-gap: ${theme.spacing.md};
  width: 100%;
`;

const ChoiceButton = styled.button<{ selected?: boolean; correct?: boolean; incorrect?: boolean; disabled?: boolean }>`
  background-color: ${props => {
    if (props.correct) return 'rgba(163, 190, 140, 0.2)';
    if (props.incorrect) return 'rgba(191, 97, 106, 0.2)';
    if (props.selected) return theme.colors.frost0;
    return theme.colors.snow1;
  }};
  color: ${theme.colors.textDark};
  border: 2px solid ${props => {
    if (props.correct) return theme.colors.aurora4;
    if (props.incorrect) return theme.colors.aurora0;
    if (props.selected) return theme.colors.frost3;
    return 'transparent';
  }};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.lg};
  font-size: 1.1rem;
  text-align: left;
  cursor: ${props => props.disabled ? 'default' : 'pointer'};
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
  
  &:hover {
    background-color: ${props => {
      if (props.disabled) {
        if (props.correct) return 'rgba(163, 190, 140, 0.2)';
        if (props.incorrect) return 'rgba(191, 97, 106, 0.2)';
        return theme.colors.snow1;
      }
      return theme.colors.frost0;
    }};
  }
  
  &::after {
    content: ${props => {
      if (props.correct) return '"✓"';
      if (props.incorrect) return '"✗"';
      return '""';
    }};
    position: absolute;
    right: ${theme.spacing.md};
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.5rem;
    color: ${props => {
      if (props.correct) return theme.colors.aurora4;
      if (props.incorrect) return theme.colors.aurora0;
      return 'transparent';
    }};
  }
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

const NextButton = styled.button`
  background-color: ${theme.colors.frost3};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.md} ${theme.spacing.lg};
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: ${theme.spacing.lg};
  
  &:hover {
    background-color: ${theme.colors.frost2};
  }
  
  &:disabled {
    background-color: ${theme.colors.disabled};
    cursor: not-allowed;
  }
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

const FeedbackText = styled.div<{ correct: boolean }>`
  margin-top: ${theme.spacing.lg};
  font-size: 1.2rem;
  font-weight: bold;
  color: ${props => props.correct ? theme.colors.aurora4 : theme.colors.aurora0};
  text-align: center;
`;

const ErrorMessage = styled.div`
  color: ${theme.colors.error};
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

const MultipleChoiceActivity: React.FC<{ words: Word[]; groupId: string }> = ({ words, groupId }) => {
  const [wordsToStudy, setWordsToStudy] = useState<Word[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [options, setOptions] = useState<Word[]>([]);
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{ shown: boolean; correct: boolean }>({ shown: false, correct: false });
  const [completed, setCompleted] = useState(false);
  const [correctCount, setCorrectCount] = useState(0);
  const [wrongCount, setWrongCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  
  useEffect(() => {
    if (words && words.length > 0) {
      console.log("Preparing multiple choice with", words.length, "words");
      const shuffled = [...words].sort(() => 0.5 - Math.random());
      const limitedWords = shuffled.slice(0, Math.min(20, shuffled.length));
      setWordsToStudy(limitedWords);
      setLoading(false);
    } else {
      console.error("No words available for multiple choice");
      setLoading(false);
    }
  }, [words]);
  
  useEffect(() => {
    if (wordsToStudy.length > 0 && words.length >= 4) {
      generateOptions();
    }
  }, [wordsToStudy, currentIndex, words.length]);
  
  const generateOptions = () => {
    if (!wordsToStudy[currentIndex] || words.length < 4) {
      return;
    }
    
    const currentWord = wordsToStudy[currentIndex];
    const otherWords = words.filter(word => word.id !== currentWord.id);
    
    if (otherWords.length < 3) {
      const allOptions = [...otherWords, currentWord].sort(() => 0.5 - Math.random());
      setOptions(allOptions);
      return;
    }
    
    const shuffledOptions = [...otherWords].sort(() => 0.5 - Math.random()).slice(0, 3);
    
    const allOptions = [...shuffledOptions, currentWord].sort(() => 0.5 - Math.random());
    setOptions(allOptions);
  };
  
  const handleSelectOption = (optionId: string) => {
    if (feedback.shown) return;
    
    setSelectedOption(optionId);
    const currentWord = wordsToStudy[currentIndex];
    const isCorrect = optionId === currentWord.id;
    
    setFeedback({ shown: true, correct: isCorrect });
    
    if (isCorrect) {
      setCorrectCount(prev => prev + 1);
    } else {
      setWrongCount(prev => prev + 1);
    }
  };
  
  const handleNextQuestion = () => {
    setSelectedOption(null);
    setFeedback({ shown: false, correct: false });
    
    if (currentIndex < wordsToStudy.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      setCompleted(true);
    }
  };
  
  const handleReturnToActivities = () => {
    navigate('/study');
  };
  
  const handleStudyAgain = () => {
    setCurrentIndex(0);
    setSelectedOption(null);
    setFeedback({ shown: false, correct: false });
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
    return <LoadingIndicator text="Preparing questions..." />;
  }
  
  if (!wordsToStudy || wordsToStudy.length === 0 || words.length < 4) {
    return (
      <Container>
        <ErrorMessage>
          {words.length < 4 
            ? "Multiple choice requires at least 4 words in the group. Please select a different group."
            : "No words available for this group. Please select a different group."
          }
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
              <StatLabel>Total Questions</StatLabel>
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
  
  if (options.length === 0) {
    return <LoadingIndicator text="Preparing question options..." />;
  }
  
  return (
    <Container>
      <ProgressContainer>
        <ProgressBar>
          <ProgressFill width={progress} />
        </ProgressBar>
        <ProgressText>
          <span>Question {currentIndex + 1} of {wordsToStudy.length}</span>
          <span>{Math.round(progress)}% Complete</span>
        </ProgressText>
      </ProgressContainer>
      
      <QuestionCard>
        <Question>
          <QuestionText>{currentWord.japanese}</QuestionText>
          <RomajiText>{currentWord.romaji}</RomajiText>
        </Question>
        
        <ChoicesContainer>
          {options.map(option => {
            const isSelected = selectedOption === option.id;
            const isCorrect = feedback.shown && option.id === currentWord.id;
            const isIncorrect = feedback.shown && isSelected && option.id !== currentWord.id;
            
            return (
              <ChoiceButton
                key={option.id}
                selected={isSelected}
                correct={isCorrect}
                incorrect={isIncorrect}
                disabled={feedback.shown}
                onClick={() => handleSelectOption(option.id)}
              >
                {option.english}
              </ChoiceButton>
            );
          })}
        </ChoicesContainer>
        
        {feedback.shown && (
          <FeedbackText correct={feedback.correct}>
            {feedback.correct ? 'Correct!' : `Incorrect. The correct answer is "${currentWord.english}".`}
          </FeedbackText>
        )}
      </QuestionCard>
      
      {feedback.shown && (
        <NextButton onClick={handleNextQuestion}>
          {currentIndex < wordsToStudy.length - 1 ? 'Next Question' : 'View Results'}
        </NextButton>
      )}
    </Container>
  );
};

export default MultipleChoiceActivity; 