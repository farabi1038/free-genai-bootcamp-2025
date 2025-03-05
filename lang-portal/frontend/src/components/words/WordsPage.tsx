import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import wordService from '../../api/wordService';
import { Word } from '../../api/types';
import LoadingIndicator from '../ui/LoadingIndicator';

const Container = styled.div`
  padding: ${theme.spacing.lg};
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: ${theme.spacing.lg};
`;

const Title = styled.h1`
  color: ${theme.colors.textDark};
  margin: 0;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const TableHeader = styled.th`
  padding: ${theme.spacing.md};
  text-align: left;
  background-color: ${theme.colors.polarNight1};
  color: ${theme.colors.snow0};
  font-weight: bold;
`;

const TableRow = styled.tr`
  &:nth-child(even) {
    background-color: ${theme.colors.snow1};
  }
  
  &:hover {
    background-color: ${theme.colors.frost0};
  }
`;

const TableCell = styled.td`
  padding: ${theme.spacing.md};
  border-bottom: 1px solid ${theme.colors.snow1};
`;

const JapaneseWord = styled(Link)`
  color: ${theme.colors.frost3};
  text-decoration: none;
  font-weight: bold;
  
  &:hover {
    text-decoration: underline;
  }
`;

const Pagination = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: ${theme.spacing.xl};
  gap: ${theme.spacing.md};
`;

const PageButton = styled.button<{ active?: boolean }>`
  background-color: ${props => props.active ? theme.colors.frost3 : theme.colors.snow1};
  color: ${props => props.active ? 'white' : theme.colors.textDark};
  border: none;
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  font-size: 0.9rem;
  cursor: pointer;
  min-width: 36px;
  
  &:hover {
    background-color: ${props => props.active ? theme.colors.frost3 : theme.colors.frost1};
  }
  
  &:disabled {
    background-color: ${theme.colors.disabled};
    cursor: not-allowed;
  }
`;

const PageInfo = styled.div`
  margin: ${theme.spacing.md} 0;
  color: ${theme.colors.textLight};
  text-align: center;
`;

const ErrorMessage = styled.div`
  background-color: ${theme.colors.aurora0};
  color: white;
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  margin-bottom: ${theme.spacing.md};
`;

const SearchForm = styled.form`
  display: flex;
  gap: ${theme.spacing.sm};
  margin-left: auto;
`;

const SearchInput = styled.input`
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  border: 1px solid ${theme.colors.snow3};
  width: 250px;
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.frost2};
    box-shadow: 0 0 0 2px rgba(94, 129, 172, 0.2);
  }
`;

const SearchButton = styled.button`
  background-color: ${theme.colors.frost3};
  color: white;
  border: none;
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  cursor: pointer;
  
  &:hover {
    background-color: ${theme.colors.frost2};
  }
`;

const ClearButton = styled.button`
  background-color: ${theme.colors.snow1};
  color: ${theme.colors.textDark};
  border: none;
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  cursor: pointer;
  
  &:hover {
    background-color: ${theme.colors.snow2};
  }
`;

const WordsPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [words, setWords] = useState<Word[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalWords, setTotalWords] = useState(0);
  
  // Get search query from URL parameters
  const queryParams = new URLSearchParams(location.search);
  const searchQuery = queryParams.get('search') || '';
  
  // Add state for search input
  const [searchInput, setSearchInput] = useState(searchQuery);
  
  const totalPages = Math.ceil(totalWords / 100);
  
  useEffect(() => {
    const fetchWords = async () => {
      try {
        setLoading(true);
        
        // Update the call to include search
        const data = await wordService.getAllWords(currentPage, 100, searchQuery);
        setWords(data.words);
        setTotalWords(data.total);
        setError(null);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchWords();
  }, [currentPage, searchQuery]);
  
  // Update search input when URL search param changes
  useEffect(() => {
    setSearchInput(searchQuery);
  }, [searchQuery]);
  
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Update URL with search query
    navigate(`/words?search=${encodeURIComponent(searchInput)}`);
  };
  
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchInput(e.target.value);
  };
  
  const handleClearSearch = () => {
    setSearchInput('');
    navigate('/words');
  };
  
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo(0, 0);
  };
  
  const renderPagination = () => {
    const pageButtons = [];
    
    // Previous button
    pageButtons.push(
      <PageButton
        key="prev"
        onClick={() => handlePageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        &laquo;
      </PageButton>
    );
    
    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, startPage + 4);
    
    for (let i = startPage; i <= endPage; i++) {
      pageButtons.push(
        <PageButton
          key={i}
          active={currentPage === i}
          onClick={() => handlePageChange(i)}
        >
          {i}
        </PageButton>
      );
    }
    
    // Next button
    pageButtons.push(
      <PageButton
        key="next"
        onClick={() => handlePageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
      >
        &raquo;
      </PageButton>
    );
    
    return pageButtons;
  };
  
  if (loading && words.length === 0) {
    return (
      <Container>
        <LoadingIndicator text="Loading words..." />
      </Container>
    );
  }
  
  return (
    <Container>
      <Header>
        <Title>Words</Title>
        <SearchForm onSubmit={handleSearchSubmit}>
          <SearchInput 
            type="text"
            placeholder="Search words..."
            value={searchInput}
            onChange={handleSearchChange}
          />
          {searchInput && (
            <ClearButton type="button" onClick={handleClearSearch}>
              Clear
            </ClearButton>
          )}
          <SearchButton type="submit">Search</SearchButton>
        </SearchForm>
      </Header>
      
      {error && (
        <ErrorMessage>
          Error loading words: {error.message}
        </ErrorMessage>
      )}
      
      <PageInfo>
        Showing {words.length} words (page {currentPage} of {totalPages})
      </PageInfo>
      
      <Table>
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
      </Table>
      
      {loading && <LoadingIndicator text="Loading more words..." />}
      
      {totalPages > 1 && (
        <Pagination>
          {renderPagination()}
        </Pagination>
      )}
    </Container>
  );
};

export default WordsPage; 