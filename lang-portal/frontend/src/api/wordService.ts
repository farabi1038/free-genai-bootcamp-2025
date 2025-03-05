import apiService from './apiService';
import { Word } from './types';
import { mockWordService } from './mockService';
import { delay } from './utils';

// Use this flag to switch between real and mock API
const USE_MOCK_API = true;

const WordService = {
  getAllWords: async (page: number = 1, limit: number = 100, search: string = ''): Promise<{words: Word[], total: number}> => {
    if (USE_MOCK_API) {
      await delay(600);
      let filteredWords = mockWords;
      
      // Apply search filter if search is provided
      if (search) {
        const searchLower = search.toLowerCase();
        filteredWords = mockWords.filter(word => 
          word.japanese.toLowerCase().includes(searchLower) ||
          word.romaji.toLowerCase().includes(searchLower) ||
          word.english.toLowerCase().includes(searchLower)
        );
      }
      
      const start = (page - 1) * limit;
      const end = start + limit;
      return {
        words: filteredWords.slice(start, end),
        total: filteredWords.length
      };
    }
    
    // Add search param to API call
    try {
      const response = await fetch(`/api/words?page=${page}&limit=${limit}&search=${encodeURIComponent(search)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching words:', error);
      throw error;
    }
  },
  
  getWordById: async (id: string): Promise<Word> => {
    if (USE_MOCK_API) {
      return mockWordService.getWordById(id);
    } else {
      return apiService.get<Word>(`/words/${id}`);
    }
  }
};

export default WordService; 