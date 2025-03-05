import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import LoadingIndicator from './ui/LoadingIndicator';
import { theme } from '../styles/theme';

const WordsContainer = styled.div`
  background-color: ${theme.colors.card};
  border-radius: ${theme.borderRadius.md};
  box-shadow: ${theme.shadows.md};
  padding: ${theme.spacing.lg};
  margin-top: ${theme.spacing.lg};
  border: 1px solid ${theme.colors.border};
`;

const WordsTable = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.th`
  text-align: left;
  padding: ${theme.spacing.md} ${theme.spacing.sm};
  border-bottom: 2px solid ${theme.colors.border};
  color: ${theme.colors.polar3};
  font-weight: 600;
`;

const TableRow = styled.tr`
  &:nth-child(even) {
    background-color: ${theme.colors.background};
  }
  
  &:hover {
    background-color: ${theme.colors.snow1};
  }
`;

const TableCell = styled.td`
  padding: ${theme.spacing.md} ${theme.spacing.sm};
  border-bottom: 1px solid ${theme.colors.border};
  color: ${theme.colors.text};
`;

const JapaneseWord = styled(Link)`
  font-weight: 600;
  color: ${theme.colors.frost4};
  text-decoration: none;
  
  &:hover {
    text-decoration: underline;
    color: ${theme.colors.primary};
  }
`;

const PaginationContainer = styled.div`
  display: flex;
  justify-content: center;
  margin-top: ${theme.spacing.lg};
`;

const PageButton = styled.button`
  background: ${props => props.disabled ? theme.colors.snow1 : 'white'};
  border: 1px solid ${theme.colors.border};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  margin: 0 ${theme.spacing.xs};
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  border-radius: ${theme.borderRadius.sm};
  color: ${props => props.disabled ? theme.colors.textLight : theme.colors.text};
  
  &:hover:not(:disabled) {
    background-color: ${theme.colors.snow2};
  }
`;

const PageHeading = styled.h1`
  color: ${theme.colors.polar1};
  margin-bottom: ${theme.spacing.lg};
  font-size: 2.2rem;
`;

// Sample data for testing
const sampleWords = [
  { id: '1', japanese: '犬', romaji: 'inu', english: 'dog', correct_count: 8, wrong_count: 2 },
  { id: '2', japanese: '猫', romaji: 'neko', english: 'cat', correct_count: 12, wrong_count: 1 },
  { id: '3', japanese: '魚', romaji: 'sakana', english: 'fish', correct_count: 5, wrong_count: 3 },
  { id: '4', japanese: '鳥', romaji: 'tori', english: 'bird', correct_count: 7, wrong_count: 0 },
  { id: '5', japanese: '水', romaji: 'mizu', english: 'water', correct_count: 10, wrong_count: 2 },
  { id: '6', japanese: '火', romaji: 'hi', english: 'fire', correct_count: 6, wrong_count: 1 },
  { id: '7', japanese: '山', romaji: 'yama', english: 'mountain', correct_count: 4, wrong_count: 1 },
  { id: '8', japanese: '川', romaji: 'kawa', english: 'river', correct_count: 9, wrong_count: 2 },
  { id: '9', japanese: '子供', romaji: 'kodomo', english: 'child', correct_count: 3, wrong_count: 4 },
  { id: '10', japanese: '家', romaji: 'ie', english: 'house', correct_count: 11, wrong_count: 0 },
];

const Words = () => {
  const [loading, setLoading] = useState(true);
  const [words, setWords] = useState(sampleWords);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(3); // Mock total pages
  
  useEffect(() => {
    // Simulate API call with loading state
    const fetchWords = async () => {
      setLoading(true);
      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      setWords(sampleWords);
      setLoading(false);
    };
    
    fetchWords();
  }, [currentPage]);
  
  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(prev => prev - 1);
    }
  };
  
  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(prev => prev + 1);
    }
  };
  
  if (loading) {
    return <LoadingIndicator text="Loading words..." />;
  }
  
  return (
    <>
      <h1>Words</h1>
      <WordsContainer>
        <WordsTable>
          <thead>
            <tr>
              <TableHeader>Japanese</TableHeader>
              <TableHeader>Romaji</TableHeader>
              <TableHeader>English</TableHeader>
              <TableHeader>Correct</TableHeader>
              <TableHeader>Wrong</TableHeader>
            </tr>
          </thead>
          <tbody>
            {words.map(word => (
              <TableRow key={word.id}>
                <TableCell>
                  <JapaneseWord to={`/words/${word.id}`}>{word.japanese}</JapaneseWord>
                </TableCell>
                <TableCell>{word.romaji}</TableCell>
                <TableCell>{word.english}</TableCell>
                <TableCell>{word.correct_count}</TableCell>
                <TableCell>{word.wrong_count}</TableCell>
              </TableRow>
            ))}
          </tbody>
        </WordsTable>
        
        <PaginationContainer>
          <PageButton 
            onClick={handlePreviousPage} 
            disabled={currentPage === 1}
          >
            Previous
          </PageButton>
          <span style={{ margin: '0 10px', lineHeight: '36px' }}>
            Page {currentPage} of {totalPages}
          </span>
          <PageButton 
            onClick={handleNextPage} 
            disabled={currentPage === totalPages}
          >
            Next
          </PageButton>
        </PaginationContainer>
      </WordsContainer>
    </>
  );
};

export default Words; 