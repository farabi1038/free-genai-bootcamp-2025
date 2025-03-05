import apiService from './apiService';
import { Group, Word, StudySession } from './types';
import { mockGroupService } from './mockService';

// Use this flag to switch between real and mock API
const USE_MOCK_API = true;

// Simple cache implementation
const cache = {
  groups: new Map<string, { data: Group, timestamp: number }>(),
  groupWords: new Map<string, { data: Word[], timestamp: number }>(),
  groupSessions: new Map<string, { data: StudySession[], timestamp: number }>(),
  allGroups: { data: null as Group[] | null, timestamp: 0 },
  
  // Cache expiration time (5 minutes)
  EXPIRATION_TIME: 5 * 60 * 1000,
  
  isExpired(timestamp: number): boolean {
    return Date.now() - timestamp > this.EXPIRATION_TIME;
  },
  
  clearCache() {
    this.groups.clear();
    this.groupWords.clear();
    this.groupSessions.clear();
    this.allGroups = { data: null, timestamp: 0 };
  }
};

const GroupService = {
  getAllGroups: async (): Promise<Group[]> => {
    // Check cache first
    if (cache.allGroups.data && !cache.isExpired(cache.allGroups.timestamp)) {
      console.log('Using cached groups data');
      return cache.allGroups.data;
    }
    
    // Fetch fresh data
    let data: Group[];
    if (USE_MOCK_API) {
      data = await mockGroupService.getAllGroups();
    } else {
      data = await apiService.get<Group[]>('/groups');
    }
    
    // Update cache
    cache.allGroups = {
      data,
      timestamp: Date.now()
    };
    
    return data;
  },
  
  getGroupById: async (id: string): Promise<Group> => {
    // Check cache first
    if (cache.groups.has(id) && !cache.isExpired(cache.groups.get(id)!.timestamp)) {
      console.log(`Using cached data for group ${id}`);
      return cache.groups.get(id)!.data;
    }
    
    // Fetch fresh data
    let data: Group;
    if (USE_MOCK_API) {
      data = await mockGroupService.getGroupById(id);
    } else {
      data = await apiService.get<Group>(`/groups/${id}`);
    }
    
    // Update cache
    cache.groups.set(id, {
      data,
      timestamp: Date.now()
    });
    
    return data;
  },
  
  getWordsByGroupId: async (id: string): Promise<Word[]> => {
    // Check cache first
    if (cache.groupWords.has(id) && !cache.isExpired(cache.groupWords.get(id)!.timestamp)) {
      console.log(`Using cached words for group ${id}`);
      return cache.groupWords.get(id)!.data;
    }
    
    // Fetch fresh data
    let data: Word[];
    if (USE_MOCK_API) {
      data = await mockGroupService.getWordsByGroupId(id);
    } else {
      data = await apiService.get<Word[]>(`/groups/${id}/words`);
    }
    
    // Update cache
    cache.groupWords.set(id, {
      data,
      timestamp: Date.now()
    });
    
    return data;
  },
  
  getStudySessionsByGroupId: async (id: string): Promise<StudySession[]> => {
    // Check cache first
    if (cache.groupSessions.has(id) && !cache.isExpired(cache.groupSessions.get(id)!.timestamp)) {
      console.log(`Using cached sessions for group ${id}`);
      return cache.groupSessions.get(id)!.data;
    }
    
    // Fetch fresh data
    let data: StudySession[];
    if (USE_MOCK_API) {
      data = await mockGroupService.getStudySessionsByGroupId(id);
    } else {
      data = await apiService.get<StudySession[]>(`/groups/${id}/study_sessions`);
    }
    
    // Update cache
    cache.groupSessions.set(id, {
      data,
      timestamp: Date.now()
    });
    
    return data;
  },
  
  clearCache: () => {
    cache.clearCache();
  }
};

export default GroupService; 