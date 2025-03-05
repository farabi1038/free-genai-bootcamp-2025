import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { theme } from '../../../styles/theme';
import { Word, Group } from '../../../api/types';
import { shuffleArray } from '../../../utils/arrayUtils';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 1000px;
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

const GameGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: ${theme.spacing.md};
  margin-bottom: ${theme.spacing.xl};
  width: 100%;
`;

const Card = styled.div<{ flipped: boolean; matched: boolean }>`
  position: relative;
  height: 120px;
  perspective: 1000px;
  cursor: ${props => (props.matched ? 'default' : 'pointer')};
  transition: transform 0.2s;
  
  &:hover {
    transform: ${props => (props.matched ? 'none' : 'scale(1.02)')};
  }
`;

const CardInner = styled.div<{ flipped: boolean }>`
  position: relative;
  width: 100%;
  height: 100%;
  text-align: center;
  transition: transform 0.6s;
  transform-style: preserve-3d;
  transform: ${props => (props.flipped ? 'rotateY(180deg)' : 'rotateY(0deg)')};
`;

const CardFace = styled.div`
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: ${theme.borderRadius};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  font-size: 1.2rem;
  font-weight: bold;
  padding: ${theme.spacing.md};
  word-break: break-word;
`;

const CardBack = styled(CardFace)`
  background-color: ${theme.colors.polarNight1};
  color: ${theme.colors.snow0};
`;

const CardFront = styled(CardFace)<{ matched: boolean }>`
  background-color: ${props => (props.matched ? theme.colors.aurora3 : theme.colors.snow0)};
  color: ${props => (props.matched ? 'white' : theme.colors.textDark)};
  transform: rotateY(180deg);
`;

const Timer = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
  color: ${theme.colors.frost3};
  margin-bottom: ${theme.spacing.md};
`;

const GameInfo = styled.div`
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-bottom: ${theme.spacing.lg};
`;

const InfoItem = styled.div`
  text-align: center;
  padding: ${theme.spacing.md};
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  min-width: 120px;
`;

const InfoLabel = styled.div`
  font-size: 0.9rem;
  color: ${theme.colors.textLight};
`;

const InfoValue = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
  color: ${theme.colors.textDark};
`;

const MatchedPairsDisplay = styled.div`
  margin-top: ${theme.spacing.lg};
  padding: ${theme.spacing.lg};
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  width: 100%;
`;

const MatchedPairsTitle = styled.h3`
  margin-bottom: ${theme.spacing.md};
  color: ${theme.colors.textDark};
`;

const MatchedPairsList = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: ${theme.spacing.md};
`;

const MatchedPair = styled.div`
  display: flex;
  justify-content: space-between;
  padding: ${theme.spacing.sm};
  border-bottom: 1px solid ${theme.colors.snow1};
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

const ResultBox = styled.div`
  background-color: ${theme.colors.frost3};
  color: white;
  padding: ${theme.spacing.lg};
  border-radius: ${theme.borderRadius};
  text-align: center;
  width: 150px;
`;

const ResultNumber = styled.div`
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: ${theme.spacing.sm};
`;

const ResultLabel = styled.div`
  font-size: 0.9rem;
`;

interface MatchingActivityProps {
  words: Word[];
  groups: Group[];
}

interface CardItem {
  id: string;
  word: Word;
  type: 'japanese' | 'english';
  flipped: boolean;
  matched: boolean;
}

const MatchingActivity: React.FC<MatchingActivityProps> = ({ words, groups }) => {
  const [cards, setCards] = useState<CardItem[]>([]);
  const [flippedCards, setFlippedCards] = useState<CardItem[]>([]);
  const [matchedPairs, setMatchedPairs] = useState<Word[]>([]);
  const [moves, setMoves] = useState(0);
  const [gameStarted, setGameStarted] = useState(false);
  const [gameCompleted, setGameCompleted] = useState(false);
  const [timer, setTimer] = useState(0);
  const [timerInterval, setTimerInterval] = useState<NodeJS.Timeout | null>(null);

  // Setup game
  useEffect(() => {
    setupGame();
  }, [words]);

  // Setup timer
  useEffect(() => {
    if (gameStarted && !gameCompleted) {
      const interval = setInterval(() => {
        setTimer(prevTimer => prevTimer + 1);
      }, 1000);
      setTimerInterval(interval);
      return () => clearInterval(interval);
    } else if (gameCompleted && timerInterval) {
      clearInterval(timerInterval);
    }
  }, [gameStarted, gameCompleted]);

  // Check for completed game
  useEffect(() => {
    if (matchedPairs.length > 0 && matchedPairs.length === words.length && gameStarted) {
      setGameCompleted(true);
    }
  }, [matchedPairs, words.length, gameStarted]);

  // Check for matches when two cards are flipped
  useEffect(() => {
    if (flippedCards.length === 2) {
      // Start the game on first move
      if (!gameStarted) {
        setGameStarted(true);
      }
      
      // Increment moves
      setMoves(prevMoves => prevMoves + 1);
      
      const [firstCard, secondCard] = flippedCards;
      
      // Check if the cards match (same word, different types)
      if (firstCard.word.id === secondCard.word.id && firstCard.type !== secondCard.type) {
        // Mark cards as matched
        setCards(prevCards => 
          prevCards.map(card => 
            card.id === firstCard.id || card.id === secondCard.id
              ? { ...card, matched: true }
              : card
          )
        );
        
        // Add to matched pairs if not already there
        setMatchedPairs(prevMatches => {
          if (!prevMatches.some(word => word.id === firstCard.word.id)) {
            return [...prevMatches, firstCard.word];
          }
          return prevMatches;
        });
        
        // Reset flipped cards
        setFlippedCards([]);
      } else {
        // If no match, flip cards back after a delay
        setTimeout(() => {
          setCards(prevCards => 
            prevCards.map(card => 
              card.id === firstCard.id || card.id === secondCard.id
                ? { ...card, flipped: false }
                : card
            )
          );
          setFlippedCards([]);
        }, 1000);
      }
    }
  }, [flippedCards, gameStarted]);

  const setupGame = () => {
    // Take at most 8 words to create 16 cards (8 pairs)
    const gameWords = shuffleArray(words).slice(0, 8);
    
    // Create card pairs (Japanese and English for each word)
    const cardPairs = gameWords.flatMap(word => [
      {
        id: `japanese-${word.id}`,
        word,
        type: 'japanese' as const,
        flipped: false,
        matched: false
      },
      {
        id: `english-${word.id}`,
        word,
        type: 'english' as const,
        flipped: false,
        matched: false
      }
    ]);
    
    // Shuffle the cards
    setCards(shuffleArray(cardPairs));
    setFlippedCards([]);
    setMatchedPairs([]);
    setMoves(0);
    setTimer(0);
    setGameStarted(false);
    setGameCompleted(false);
  };

  const handleCardClick = (clickedCard: CardItem) => {
    // Ignore clicks if card is already flipped, matched, or two cards are already flipped
    if (
      clickedCard.flipped || 
      clickedCard.matched || 
      flippedCards.length >= 2 ||
      gameCompleted
    ) {
      return;
    }
    
    // Flip the card
    setCards(prevCards => 
      prevCards.map(card => 
        card.id === clickedCard.id ? { ...card, flipped: true } : card
      )
    );
    
    // Add to flipped cards
    setFlippedCards(prevFlipped => [...prevFlipped, clickedCard]);
  };

  const restartGame = () => {
    setupGame();
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (gameCompleted) {
    return (
      <Container>
        <CompletionMessage>
          <h2>Game Complete!</h2>
          
          <ResultsSummary>
            <ResultBox>
              <ResultNumber>{matchedPairs.length}</ResultNumber>
              <ResultLabel>Pairs Matched</ResultLabel>
            </ResultBox>
            <ResultBox>
              <ResultNumber>{moves}</ResultNumber>
              <ResultLabel>Moves</ResultLabel>
            </ResultBox>
            <ResultBox>
              <ResultNumber>{formatTime(timer)}</ResultNumber>
              <ResultLabel>Time</ResultLabel>
            </ResultBox>
          </ResultsSummary>
          
          <p>You matched all pairs in {moves} moves and {formatTime(timer)}!</p>
          
          <Button onClick={restartGame} style={{ marginTop: theme.spacing.lg }}>
            Play Again
          </Button>
        </CompletionMessage>
      </Container>
    );
  }

  return (
    <Container>
      <Header>
        <Title>Matching Game</Title>
        <StatsContainer>
          <p>Studying words from {groups.length} groups</p>
        </StatsContainer>
      </Header>
      
      <GameInfo>
        <InfoItem>
          <InfoValue>{matchedPairs.length}/{cards.length/2}</InfoValue>
          <InfoLabel>Pairs Matched</InfoLabel>
        </InfoItem>
        <InfoItem>
          <InfoValue>{moves}</InfoValue>
          <InfoLabel>Moves</InfoLabel>
        </InfoItem>
        <InfoItem>
          <InfoValue>{formatTime(timer)}</InfoValue>
          <InfoLabel>Time</InfoLabel>
        </InfoItem>
      </GameInfo>
      
      <ProgressBar>
        <Progress width={(matchedPairs.length / (cards.length/2)) * 100} />
      </ProgressBar>
      
      <GameGrid>
        {cards.map(card => (
          <Card 
            key={card.id} 
            flipped={card.flipped} 
            matched={card.matched}
            onClick={() => handleCardClick(card)}
          >
            <CardInner flipped={card.flipped || card.matched}>
              <CardBack>{/* Question mark or card back design */}?</CardBack>
              <CardFront matched={card.matched}>
                {card.type === 'japanese' ? card.word.japanese : card.word.english}
              </CardFront>
            </CardInner>
          </Card>
        ))}
      </GameGrid>
      
      <Button onClick={restartGame}>
        Restart Game
      </Button>
      
      {matchedPairs.length > 0 && (
        <MatchedPairsDisplay>
          <MatchedPairsTitle>Matched Pairs</MatchedPairsTitle>
          <MatchedPairsList>
            {matchedPairs.map(word => (
              <MatchedPair key={word.id}>
                <span>{word.japanese}</span>
                <span>{word.english}</span>
              </MatchedPair>
            ))}
          </MatchedPairsList>
        </MatchedPairsDisplay>
      )}
    </Container>
  );
};

export default MatchingActivity; 