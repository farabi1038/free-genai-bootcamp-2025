import apiService from './apiService';

export interface LastStudySession {
  id: number;
  group_id: number;
  group_name: string;
  date: string;
  score: number;
  total: number;
}

export interface StudyProgress {
  total_words: number;
  words_studied: number;
  words_mastered: number;
  completion_rate: number;
}

export interface QuickStats {
  total_groups: number;
  total_words: number;
  total_sessions: number;
  average_score: number;
}

// Set to false to use the real API
const USE_MOCK_API = false;

const getDashboardService = () => {
  return {
    getLastStudySession: async (): Promise<LastStudySession | null> => {
      if (USE_MOCK_API) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Return mock data for development
        return {
          id: 1,
          group_id: 2,
          group_name: "Basic Phrases",
          date: "2023-06-15T14:30:00Z",
          score: 8,
          total: 10
        };
      }
      
      try {
        const response = await apiService.get<LastStudySession | null>('/last_session');
        return response;
      } catch (error) {
        console.error('Error fetching last study session:', error);
        throw error;
      }
    },
    
    getStudyProgress: async (): Promise<StudyProgress> => {
      if (USE_MOCK_API) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Return mock data for development
        return {
          total_words: 200,
          words_studied: 85,
          words_mastered: 42,
          completion_rate: 21
        };
      }
      
      try {
        const response = await apiService.get<StudyProgress>('/progress');
        return response;
      } catch (error) {
        console.error('Error fetching study progress:', error);
        throw error;
      }
    },
    
    getQuickStats: async (): Promise<QuickStats> => {
      if (USE_MOCK_API) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Return mock data for development
        return {
          total_groups: 5,
          total_words: 200,
          total_sessions: 15,
          average_score: 76
        };
      }
      
      try {
        const response = await apiService.get<QuickStats>('/stats');
        return response;
      } catch (error) {
        console.error('Error fetching quick stats:', error);
        throw error;
      }
    }
  };
};

const dashboardService = getDashboardService();
export default dashboardService; 