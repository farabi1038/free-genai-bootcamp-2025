import { Word, Group, StudySession } from './types';
import { delay } from './utils';
import mockService from './mockService';

export interface SearchResult {
  words: {
    results: Word[];
    total: number;
  };
  groups: {
    results: Group[];
    total: number;
  };
  sessions: {
    results: StudySession[];
    total: number;
  };
}

const USE_MOCK_API = true;

const SearchService = {
  search: async (query: string): Promise<SearchResult> => {
    if (USE_MOCK_API) {
      await delay(600);
      
      // Get mock data
      const allWords = await mockService.getAllWords();
      const allGroups = await mockService.getAllGroups();
      const { sessions: allSessions } = await mockService.getAllStudySessions();
      
      // Filter words
      const matchedWords = allWords.filter(word => 
        word.japanese.toLowerCase().includes(query.toLowerCase()) ||
        word.romaji.toLowerCase().includes(query.toLowerCase()) ||
        word.english.toLowerCase().includes(query.toLowerCase())
      );
      
      // Filter groups
      const matchedGroups = allGroups.filter(group =>
        group.name.toLowerCase().includes(query.toLowerCase())
      );
      
      // Filter sessions
      const matchedSessions = allSessions.filter(session =>
        session.activity_name.toLowerCase().includes(query.toLowerCase()) ||
        session.group_name.toLowerCase().includes(query.toLowerCase())
      );
      
      return {
        words: {
          results: matchedWords.slice(0, 10), // Limit to 10 results
          total: matchedWords.length
        },
        groups: {
          results: matchedGroups.slice(0, 5),
          total: matchedGroups.length
        },
        sessions: {
          results: matchedSessions.slice(0, 5),
          total: matchedSessions.length
        }
      };
    }
    
    try {
      const response = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error performing search:', error);
      throw error;
    }
  }
};

export default SearchService; 