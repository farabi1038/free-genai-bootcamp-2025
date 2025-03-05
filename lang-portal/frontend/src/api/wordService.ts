import apiService from './apiService';
import { Word } from './types';
import { mockWordService } from './mockService';
import { delay } from './utils';

// Use this flag to switch between real and mock API
const USE_MOCK_API = false;

// Type for creating a new word
interface CreateWordRequest {
  japanese: string;
  romaji: string;
  english: string;
  group_ids?: number[];
}

const WordService = {
  getAllWords: async (page: number = 1, limit: number = 100, search: string = ''): Promise<{words: Word[], total: number}> => {
    if (USE_MOCK_API) {
      // The mock service doesn't support search, so we'll handle it here
      const result = await mockWordService.getAllWords(page, limit);
      
      if (search) {
        const searchLower = search.toLowerCase();
        const filteredWords = result.words.filter((word: Word) => 
          word.japanese.toLowerCase().includes(searchLower) ||
          word.romaji.toLowerCase().includes(searchLower) ||
          word.english.toLowerCase().includes(searchLower)
        );
        return {
          words: filteredWords,
          total: filteredWords.length
        };
      }
      
      return result;
    }
    
    // Use apiService for real API calls
    try {
      const params = { page, limit, search };
      return await apiService.get<{words: Word[], total: number}>('/words', params);
    } catch (error) {
      console.error('Error fetching words:', error);
      throw error;
    }
  },
  
  getWordById: async (id: string): Promise<Word> => {
    if (USE_MOCK_API) {
      return mockWordService.getWordById(id);
    }
    
    try {
      return await apiService.get<Word>(`/words/${id}`);
    } catch (error) {
      console.error(`Error fetching word with ID ${id}:`, error);
      throw error;
    }
  },
  
  createWord: async (wordData: CreateWordRequest): Promise<Word> => {
    if (USE_MOCK_API) {
      return mockWordService.createWord(wordData);
    }
    
    try {
      return await apiService.post<Word>('/words', wordData);
    } catch (error) {
      console.error('Error creating word:', error);
      throw error;
    }
  }
};

export default WordService; 