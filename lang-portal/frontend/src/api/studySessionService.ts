import apiService from './apiService';
import { StudySession } from './studyActivityService';

export interface WordReview {
  id: number;
  word_id: number;
  japanese: string;
  romaji: string;
  english: string;
  correct: boolean;
  created_at: string;
}

const USE_MOCK_API = false;

const getStudySessionService = () => {
  return {
    getAllStudySessions: async (page: number = 1, limit: number = 20): Promise<StudySession[]> => {
      if (USE_MOCK_API) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Return mock data for development
        return [
          {
            id: 1,
            group_id: 1,
            group_name: "Basic Phrases",
            activity_id: 1,
            activity_name: "Flashcards",
            score: 8,
            total: 10,
            created_at: "2023-06-15T14:30:00Z"
          },
          {
            id: 2,
            group_id: 2,
            group_name: "Common Nouns",
            activity_id: 2,
            activity_name: "Matching Game",
            score: 7,
            total: 10,
            created_at: "2023-06-16T10:15:00Z"
          }
        ];
      }
      
      try {
        const response = await apiService.get<StudySession[]>(`/study_sessions?page=${page}&limit=${limit}`);
        return response;
      } catch (error) {
        console.error('Error fetching study sessions:', error);
        throw error;
      }
    },
    
    getStudySessionById: async (sessionId: number): Promise<StudySession> => {
      if (USE_MOCK_API) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Return mock data for development
        return {
          id: sessionId,
          group_id: 1,
          group_name: "Basic Phrases",
          activity_id: 1,
          activity_name: "Flashcards",
          score: 8,
          total: 10,
          created_at: "2023-06-15T14:30:00Z"
        };
      }
      
      try {
        const response = await apiService.get<StudySession>(`/study_sessions/${sessionId}`);
        return response;
      } catch (error) {
        console.error(`Error fetching study session with id ${sessionId}:`, error);
        throw error;
      }
    },
    
    getStudySessionWords: async (sessionId: number): Promise<WordReview[]> => {
      if (USE_MOCK_API) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Return mock data for development
        return [
          {
            id: 1,
            word_id: 1,
            japanese: "こんにちは",
            romaji: "konnichiwa",
            english: "hello",
            correct: true,
            created_at: "2023-06-15T14:30:00Z"
          },
          {
            id: 2,
            word_id: 2,
            japanese: "さようなら",
            romaji: "sayounara",
            english: "goodbye",
            correct: false,
            created_at: "2023-06-15T14:31:00Z"
          }
        ];
      }
      
      try {
        const response = await apiService.get<WordReview[]>(`/study_sessions/${sessionId}/words`);
        return response;
      } catch (error) {
        console.error(`Error fetching words for study session ${sessionId}:`, error);
        throw error;
      }
    }
  };
};

const studySessionService = getStudySessionService();
export default studySessionService; 