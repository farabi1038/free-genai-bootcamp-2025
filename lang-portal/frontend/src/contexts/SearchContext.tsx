import React, { createContext, useState, useContext, ReactNode } from 'react';
import searchService, { SearchResult } from '../api/searchService';

interface SearchContextType {
  query: string;
  results: SearchResult | null;
  loading: boolean;
  error: Error | null;
  searchVisible: boolean;
  performSearch: (query: string) => Promise<void>;
  clearSearch: () => void;
  toggleSearchVisibility: () => void;
}

const SearchContext = createContext<SearchContextType | undefined>(undefined);

export const useSearch = () => {
  const context = useContext(SearchContext);
  if (context === undefined) {
    throw new Error('useSearch must be used within a SearchProvider');
  }
  return context;
};

interface SearchProviderProps {
  children: ReactNode;
}

export const SearchProvider: React.FC<SearchProviderProps> = ({ children }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [searchVisible, setSearchVisible] = useState(false);
  
  const performSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults(null);
      setQuery('');
      return;
    }
    
    try {
      setLoading(true);
      setQuery(searchQuery);
      const searchResults = await searchService.search(searchQuery);
      setResults(searchResults);
      setError(null);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };
  
  const clearSearch = () => {
    setQuery('');
    setResults(null);
    setError(null);
  };
  
  const toggleSearchVisibility = () => {
    setSearchVisible(prev => !prev);
    if (!searchVisible) {
      clearSearch();
    }
  };
  
  return (
    <SearchContext.Provider
      value={{
        query,
        results,
        loading,
        error,
        searchVisible,
        performSearch,
        clearSearch,
        toggleSearchVisibility
      }}
    >
      {children}
    </SearchContext.Provider>
  );
}; 