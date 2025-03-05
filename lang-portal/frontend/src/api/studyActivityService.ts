import apiService from './apiService';
import { StudyActivity } from './types';
import { mockStudyActivityService } from './mockService';

// Use this flag to switch between real and mock API
const USE_MOCK_API = true;

const StudyActivityService = {
  getAllActivities: async (): Promise<StudyActivity[]> => {
    if (USE_MOCK_API) {
      return mockStudyActivityService.getAllActivities();
    }
    return apiService.get<StudyActivity[]>('/study_activities');
  },
  
  getActivityById: async (id: string): Promise<StudyActivity> => {
    if (USE_MOCK_API) {
      return mockStudyActivityService.getActivityById(id);
    }
    return apiService.get<StudyActivity>(`/study_activities/${id}`);
  },
  
  launchActivity: async (activityId: string, groupId: string): Promise<any> => {
    if (USE_MOCK_API) {
      return mockStudyActivityService.launchActivity(activityId, groupId);
    }
    return apiService.post('/study_activities', { 
      activity_id: activityId,
      group_id: groupId 
    });
  }
};

export default StudyActivityService; 