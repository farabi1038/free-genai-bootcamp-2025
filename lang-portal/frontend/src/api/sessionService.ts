import { StudySession, StudySessionDetail, WordResult } from './types';
import mockService from './mockService';

const USE_MOCK_API = true; // Toggle between mock and real API

// We'll use the same fetch approach used in other services
// instead of importing apiRequest which doesn't exist
const SessionService = {
  getAllSessions: async (page: number = 1, limit: number = 10): Promise<{sessions: StudySession[], total: number}> => {
    if (USE_MOCK_API) {
      return mockService.getAllStudySessions(page, limit);
    }
    
    try {
      const response = await fetch(`/api/sessions?page=${page}&limit=${limit}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching sessions:', error);
      throw error;
    }
  },
  
  getSessionById: async (id: string): Promise<StudySessionDetail> => {
    if (USE_MOCK_API) {
      return mockService.getStudySessionById(id);
    }
    
    try {
      const response = await fetch(`/api/sessions/${id}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching session details:', error);
      throw error;
    }
  }
};

export default SessionService; 