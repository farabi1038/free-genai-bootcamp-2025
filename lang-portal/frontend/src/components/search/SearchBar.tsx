import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import { useSearch } from '../../contexts/SearchContext';

const SearchContainer = styled.div<{ isOpen: boolean }>`
  position: relative;
  transition: all 0.3s ease;
  width: ${props => props.isOpen ? '300px' : '40px'};
  height: 40px;
`;

const SearchInput = styled.input<{ isOpen: boolean }>`
  width: 100%;
  height: 100%;
  padding: ${props => props.isOpen ? `0 ${theme.spacing.xl} 0 ${theme.spacing.lg}` : '0'};
  border-radius: 20px;
  border: 2px solid ${theme.colors.snow1};
  background-color: ${theme.colors.snow0};
  font-size: 1rem;
  color: ${theme.colors.textDark};
  opacity: ${props => props.isOpen ? '1' : '0'};
  transition: all 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.frost2};
  }
`;

const IconButton = styled.button<{ isOpen?: boolean; position: 'left' | 'right' }>`
  position: absolute;
  top: 50%;
  ${props => props.position === 'left' ? 'left: 10px;' : 'right: 10px;'}
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: ${theme.colors.textLight};
  cursor: pointer;
  z-index: 1;
  opacity: ${props => (props.isOpen || props.position === 'left') ? '1' : '0'};
  transition: all 0.3s ease;
  font-size: 14px;
  width: 20px;
  height: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  
  &:hover {
    color: ${theme.colors.frost3};
  }
  
  &:focus {
    outline: none;
  }
`;

// Simple SVG search icon as a component
const SearchIcon = () => (
  <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8"></circle>
    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
  </svg>
);

// Simple SVG X icon as a component
const CloseIcon = () => (
  <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
);

const SearchBar: React.FC = () => {
  const { query, searchVisible, performSearch, clearSearch, toggleSearchVisibility } = useSearch();
  const [inputValue, setInputValue] = useState(query);
  const inputRef = useRef<HTMLInputElement>(null);
  
  // Focus the input when search becomes visible
  useEffect(() => {
    if (searchVisible && inputRef.current) {
      inputRef.current.focus();
    }
  }, [searchVisible]);
  
  // Update input value when query changes
  useEffect(() => {
    setInputValue(query);
  }, [query]);
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputValue(value);
  };
  
  const handleSearch = () => {
    if (!searchVisible) {
      toggleSearchVisibility();
      return;
    }
    
    performSearch(inputValue);
  };
  
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      performSearch(inputValue);
    } else if (e.key === 'Escape') {
      toggleSearchVisibility();
    }
  };
  
  const handleClear = () => {
    setInputValue('');
    clearSearch();
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };
  
  return (
    <SearchContainer isOpen={searchVisible}>
      <IconButton 
        position="left" 
        onClick={handleSearch}
        aria-label="Search"
      >
        <SearchIcon />
      </IconButton>
      <SearchInput
        ref={inputRef}
        type="text"
        placeholder="Search words, groups, sessions..."
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        isOpen={searchVisible}
        aria-label="Search"
      />
      {searchVisible && inputValue && (
        <IconButton 
          position="right" 
          isOpen={searchVisible} 
          onClick={handleClear}
          aria-label="Clear search"
        >
          <CloseIcon />
        </IconButton>
      )}
    </SearchContainer>
  );
};

export default SearchBar; 