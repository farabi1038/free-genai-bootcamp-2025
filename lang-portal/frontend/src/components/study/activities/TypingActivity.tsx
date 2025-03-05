import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { theme } from '../../../styles/theme';
import { Word, Group } from '../../../api/types';
import { shuffleArray } from '../../../utils/arrayUtils';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
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

const QuestionContainer = styled.div`
  width: 100%;
  margin-bottom: ${theme.spacing.xl};
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.lg};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const QuestionHeader = styled.div`
  text-align: center;
  margin-bottom: ${theme.spacing.xl};
`;

const QuestionWord = styled.h2`
  font-size: 2rem;
  margin-bottom: ${theme.spacing.md};
  color: ${theme.colors.polarNight0};
`;

const QuestionSubtext = styled.p`
  font-size: 1.2rem;
  color: ${theme.colors.textLight};
`;

const InputContainer = styled.div`
  margin: ${theme.spacing.xl} 0;
`;

const InputField = styled.input`
  width: 100%;
  padding: ${theme.spacing.lg};
  border: 2px solid ${theme.colors.frost1};
  border-radius: ${theme.borderRadius};
  font-size: 1.2rem;
  outline: none;
  transition: border-color 0.2s;
  
  &:focus {
    border-color: ${theme.colors.frost3};
  }
`;

const SubmitButton = styled(Button)`
  width: 100%;
  margin-top: ${theme.spacing.md};
  padding: ${theme.spacing.md};
  font-size: 1.1rem;
`;

const FeedbackContainer = styled.div<{ correct?: boolean }>`
  margin-top: ${theme.spacing.lg};
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  background-color: ${props => props.correct ? theme.colors.aurora3 : theme.colors.aurora0};
  color: white;
  text-align: center;
`;

const CorrectAnswer = styled.div`
  margin-top: ${theme.spacing.sm};
  font-weight: bold;
`;

const HintContainer = styled.div`
  margin-top: ${theme.spacing.md};
  display: flex;
  justify-content: center;
`;

const HintButton = styled(Button)`
  background-color: ${theme.colors.frost1};
  
  &:hover {
    background-color: ${theme.colors.frost2};
  }
`;

const NextButton = styled(Button)`
  background-color: ${theme.colors.frost3};
  width: 150px;
  margin-top: ${theme.spacing.lg};
  
  &:hover {
    background-color: ${theme.colors.frost2};
  }
`;

const CompletionMessage = styled.div`
  text-align: center;
  padding: ${theme.spacing.xl};
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  width: 100%;
`;

const ResultsSummary = styled.div`
  display: flex;
  justify-content: center;
  gap: ${theme.spacing.xl};
  margin: ${theme.spacing.xl} 0;
`;

const ResultBox = styled.div<{ correct?: boolean }>`
  background-color: ${props => props.correct ? theme.colors.aurora3 : theme.colors.aurora0};
  color: white;
  padding: ${theme.spacing.lg};
  border-radius: ${theme.borderRadius};
  width: 150px;
  text-align: center;
`;

const ResultNumber = styled.div`
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: ${theme.spacing.sm};
`;

const ResultLabel = styled.div`
  font-size: 0.9rem;
`;

interface TypingActivityProps {
  words: Word[];
  groups: Group[];
}

interface Question {
  questionWord: Word;
  answer: string;
}

const TypingActivity: React.FC<TypingActivityProps> = ({ words, groups }) => {
  const [direction, setDirection] = useState<'ja-en' | 'en-ja'>('ja-en');
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isAnswerChecked, setIsAnswerChecked] = useState(false);
  const [isCorrect, setIsCorrect] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [correctCount, setCorrectCount] = useState(0);
  const [incorrectCount, setIncorrectCount] = useState(0);
  const [completed, setCompleted] = useState(false);
  
  const inputRef = useRef<HTMLInputElement>(null);
  
  // Generate questions when component mounts or direction changes
  useEffect(() => {
    // Shuffle the words first
    const shuffledWords = shuffleArray([...words]);
    
    // Take up to 20 words for the exercise
    const quizWords = shuffledWords.slice(0, 20);
    
    // Generate questions from the quiz words
    const generatedQuestions = generateQuestions(quizWords, direction);
    
    // Set the questions
    setQuestions(generatedQuestions);
    
    // Reset state
    setCurrentQuestionIndex(0);
    setUserInput('');
    setIsAnswerChecked(false);
    setIsCorrect(false);
    setShowHint(false);
    setCorrectCount(0);
    setIncorrectCount(0);
    setCompleted(false);
  }, [words, direction]);
  
  // Focus the input field when a new question is presented
  useEffect(() => {
    if (!isAnswerChecked && inputRef.current) {
      inputRef.current.focus();
    }
  }, [currentQuestionIndex, isAnswerChecked]);
  
  // Generate typing questions
  const generateQuestions = (quizWords: Word[], dir: 'ja-en' | 'en-ja'): Question[] => {
    return quizWords.map(word => {
      return {
        questionWord: word,
        answer: dir === 'ja-en' ? word.english.toLowerCase() : word.japanese
      };
    });
  };
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUserInput(e.target.value);
  };
  
  const checkAnswer = () => {
    if (userInput.trim() === '') return;
    
    const currentQuestion = questions[currentQuestionIndex];
    const normalizedUserInput = userInput.trim().toLowerCase();
    const normalizedAnswer = currentQuestion.answer.toLowerCase();
    
    const answerIsCorrect = normalizedUserInput === normalizedAnswer;
    
    setIsCorrect(answerIsCorrect);
    setIsAnswerChecked(true);
    
    // Update score
    if (answerIsCorrect) {
      setCorrectCount(correctCount + 1);
    } else {
      setIncorrectCount(incorrectCount + 1);
    }
  };
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isAnswerChecked) {
      checkAnswer();
    }
  };
  
  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
      setUserInput('');
      setIsAnswerChecked(false);
      setIsCorrect(false);
      setShowHint(false);
    } else {
      setCompleted(true);
    }
  };
  
  const toggleHint = () => {
    setShowHint(!showHint);
  };
  
  const handleRestart = () => {
    // Regenerate questions with the same direction
    const shuffledWords = shuffleArray([...words]);
    const quizWords = shuffledWords.slice(0, 20);
    const generatedQuestions = generateQuestions(quizWords, direction);
    
    // Reset state
    setQuestions(generatedQuestions);
    setCurrentQuestionIndex(0);
    setUserInput('');
    setIsAnswerChecked(false);
    setIsCorrect(false);
    setShowHint(false);
    setCorrectCount(0);
    setIncorrectCount(0);
    setCompleted(false);
  };
  
  const generateHint = (answer: string): string => {
    // Create a hint by showing some characters and hiding others
    return answer.split('').map((char, index) => {
      // Show first character, every third character, and spaces
      if (index === 0 || index % 3 === 0 || char === ' ') {
        return char;
      }
      return '_';
    }).join(' ');
  };
  
  if (questions.length === 0) {
    return <Container>Loading questions...</Container>;
  }
  
  if (completed) {
    const total = correctCount + incorrectCount;
    const percentage = total > 0 ? Math.round((correctCount / total) * 100) : 0;
    
    return (
      <Container>
        <CompletionMessage>
          <h2>Typing Practice Complete!</h2>
          <p>You've completed all {questions.length} words.</p>
          
          <ResultsSummary>
            <ResultBox correct>
              <ResultNumber>{correctCount}</ResultNumber>
              <ResultLabel>Correct</ResultLabel>
            </ResultBox>
            <ResultBox>
              <ResultNumber>{incorrectCount}</ResultNumber>
              <ResultLabel>Incorrect</ResultLabel>
            </ResultBox>
          </ResultsSummary>
          
          <p>Your accuracy: {percentage}%</p>
          
          <Button onClick={handleRestart} style={{ marginTop: theme.spacing.lg }}>
            Try Again
          </Button>
        </CompletionMessage>
      </Container>
    );
  }
  
  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex) / questions.length) * 100;
  
  return (
    <Container>
      <Header>
        <Title>Typing Practice</Title>
        <StatsContainer>
          <p>Word {currentQuestionIndex + 1} of {questions.length}</p>
          <p>Score: {correctCount} correct, {incorrectCount} incorrect</p>
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
      
      <QuestionContainer>
        <QuestionHeader>
          {direction === 'ja-en' ? (
            <>
              <QuestionWord>{currentQuestion.questionWord.japanese}</QuestionWord>
              <QuestionSubtext>{currentQuestion.questionWord.romaji}</QuestionSubtext>
              <p>Type the English translation:</p>
            </>
          ) : (
            <>
              <QuestionWord>{currentQuestion.questionWord.english}</QuestionWord>
              <p>Type the Japanese word:</p>
            </>
          )}
        </QuestionHeader>
        
        <InputContainer>
          <InputField
            ref={inputRef}
            type="text"
            value={userInput}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder={`Type the ${direction === 'ja-en' ? 'English' : 'Japanese'} word...`}
            disabled={isAnswerChecked}
          />
          
          {!isAnswerChecked && (
            <SubmitButton onClick={checkAnswer}>
              Check Answer
            </SubmitButton>
          )}
        </InputContainer>
        
        {!isAnswerChecked && !showHint && (
          <HintContainer>
            <HintButton onClick={toggleHint}>
              Show Hint
            </HintButton>
          </HintContainer>
        )}
        
        {showHint && !isAnswerChecked && (
          <FeedbackContainer>
            <p>Hint: {generateHint(currentQuestion.answer)}</p>
          </FeedbackContainer>
        )}
        
        {isAnswerChecked && (
          <FeedbackContainer correct={isCorrect}>
            {isCorrect ? (
              <p>Correct! 🎉</p>
            ) : (
              <>
                <p>Not quite right. Try again next time!</p>
                <CorrectAnswer>
                  Correct answer: {currentQuestion.answer}
                </CorrectAnswer>
              </>
            )}
            
            <div style={{ display: 'flex', justifyContent: 'center', marginTop: theme.spacing.md }}>
              <NextButton onClick={handleNextQuestion}>
                Next Word
              </NextButton>
            </div>
          </FeedbackContainer>
        )}
      </QuestionContainer>
    </Container>
  );
};

export default TypingActivity; 