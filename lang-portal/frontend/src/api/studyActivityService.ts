import apiService from './apiService';

export interface StudyActivity {
  id: number;
  name: string;
  description: string;
  thumbnail_url: string;
  url: string;
  created_at: string;
  updated_at: string;
}

export interface StudySession {
  id: number;
  group_id: number;
  group_name: string;
  activity_id: number;
  activity_name: string;
  score: number;
  total: number;
  created_at: string;
}

export interface CreateStudySessionRequest {
  group_id: number;
  score: number;
  total: number;
}

export interface UpdateWordStatsRequest {
  word_id: number;
  correct: boolean;
}

export interface RecordStudyActivityRequest {
  word_id: number;
  session_id: number;
  correct: boolean;
}

const USE_MOCK_API = false;

const getStudyActivityService = () => {
  return {
    getAllStudyActivities: async (): Promise<StudyActivity[]> => {
      if (USE_MOCK_API) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Return mock data for development
        return [
          {
            id: 1,
            name: "Flashcards",
            description: "Study vocabulary with flashcards",
            thumbnail_url: "/images/flashcards.jpg",
            url: "/study/flashcards",
            created_at: "2023-01-01T00:00:00Z",
            updated_at: "2023-01-01T00:00:00Z"
          },
          {
            id: 2,
            name: "Matching Game",
            description: "Match Japanese words with their meanings",
            thumbnail_url: "/images/matching.jpg",
            url: "/study/matching",
            created_at: "2023-01-01T00:00:00Z",
            updated_at: "2023-01-01T00:00:00Z"
          }
        ];
      }
      
      try {
        const response = await apiService.get<StudyActivity[]>('/study_activities');
        return response;
      } catch (error) {
        console.error('Error fetching study activities:', error);
        throw error;
      }
    },
    
    getStudyActivityById: async (id: number): Promise<StudyActivity> => {
      if (USE_MOCK_API) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Return mock data for development
        return {
          id: id,
          name: "Flashcards",
          description: "Study vocabulary with flashcards",
          thumbnail_url: "/images/flashcards.jpg",
          url: "/study/flashcards",
          created_at: "2023-01-01T00:00:00Z",
          updated_at: "2023-01-01T00:00:00Z"
        };
      }
      
      try {
        const response = await apiService.get<StudyActivity>(`/study_activities/${id}`);
        return response;
      } catch (error) {
        console.error(`Error fetching study activity with id ${id}:`, error);
        throw error;
      }
    },
    
    getStudySessionsByActivityId: async (activityId: number): Promise<StudySession[]> => {
      if (USE_MOCK_API) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Return mock data for development
        return [
          {
            id: 1,
            group_id: 1,
            group_name: "Basic Phrases",
            activity_id: activityId,
            activity_name: "Flashcards",
            score: 8,
            total: 10,
            created_at: "2023-06-15T14:30:00Z"
          }
        ];
      }
      
      try {
        const response = await apiService.get<StudySession[]>(`/study_activities/${activityId}/study_sessions`);
        return response;
      } catch (error) {
        console.error(`Error fetching study sessions for activity ${activityId}:`, error);
        throw error;
      }
    },
    
    createStudySession: async (data: CreateStudySessionRequest): Promise<StudySession> => {
      if (USE_MOCK_API) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Return mock data for development
        return {
          id: Math.floor(Math.random() * 1000) + 1,
          group_id: data.group_id,
          group_name: "Group Name",
          activity_id: 1,
          activity_name: "Flashcards",
          score: data.score,
          total: data.total,
          created_at: new Date().toISOString()
        };
      }
      
      try {
        const response = await apiService.post<StudySession>('/study/sessions', data);
        return response;
      } catch (error) {
        console.error('Error creating study session:', error);
        throw error;
      }
    },
    
    updateWordStats: async (data: UpdateWordStatsRequest): Promise<void> => {
      if (USE_MOCK_API) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 300));
        return;
      }
      
      try {
        await apiService.post('/study/word-stats', data);
      } catch (error) {
        console.error('Error updating word stats:', error);
        throw error;
      }
    },
    
    recordStudyActivity: async (data: RecordStudyActivityRequest): Promise<void> => {
      if (USE_MOCK_API) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 300));
        return;
      }
      
      try {
        await apiService.post('/study/activities', data);
      } catch (error) {
        console.error('Error recording study activity:', error);
        throw error;
      }
    }
  };
};

const studyActivityService = getStudyActivityService();
export default studyActivityService; 