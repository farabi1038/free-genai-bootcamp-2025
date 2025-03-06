import apiService from './apiService';
import { Group, Word, StudySession } from './types';
import { delay } from './utils';

// Use this flag to switch between real and mock API
const USE_MOCK_API = false;

// Mock data for development
const mockGroups: Group[] = [
  { id: "1", name: "Basic Phrases", word_count: 25 },
  { id: "2", name: "Food and Dining", word_count: 30 },
  { id: "3", name: "Travel Essentials", word_count: 45 },
  { id: "4", name: "Business Japanese", word_count: 50 }
];

const mockWords: Word[] = [
  { id: "1", japanese: "こんにちは", romaji: "konnichiwa", english: "hello", correct_count: 10, wrong_count: 2 },
  { id: "2", japanese: "さようなら", romaji: "sayounara", english: "goodbye", correct_count: 8, wrong_count: 3 },
  { id: "3", japanese: "ありがとう", romaji: "arigatou", english: "thank you", correct_count: 12, wrong_count: 1 },
  { id: "4", japanese: "お願いします", romaji: "onegaishimasu", english: "please", correct_count: 7, wrong_count: 4 }
];

const mockSessions: StudySession[] = [
  { 
    id: "1", 
    activity_name: "Flashcards", 
    group_id: "1", 
    group_name: "Basic Phrases", 
    start_time: "2023-03-01T10:00:00Z", 
    end_time: "2023-03-01T10:15:00Z", 
    review_item_count: 20, 
    correct_count: 15, 
    wrong_count: 5 
  },
  { 
    id: "2", 
    activity_name: "Quiz", 
    group_id: "1", 
    group_name: "Basic Phrases", 
    start_time: "2023-03-02T14:00:00Z", 
    end_time: "2023-03-02T14:10:00Z", 
    review_item_count: 10, 
    correct_count: 8, 
    wrong_count: 2 
  }
];

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

// Type for creating a new group
interface CreateGroupRequest {
  name: string;
  word_ids?: number[];
}

const GroupService = {
  getAllGroups: async (page: number = 1, limit: number = 20): Promise<{groups: Group[], total: number}> => {
    if (USE_MOCK_API) {
      // Get mock data
      await delay(300);
      // Paginate mock groups
      const start = (page - 1) * limit;
      const end = Math.min(start + limit, mockGroups.length);
      return {
        groups: mockGroups.slice(start, end),
        total: mockGroups.length
      };
    }
    
    // Use real API
    try {
      const params = { page, limit };
      return await apiService.get<{groups: Group[], total: number}>('/groups', params);
    } catch (error) {
      console.error('Error fetching groups:', error);
      throw error;
    }
  },
  
  getGroupById: async (id: string): Promise<Group> => {
    if (USE_MOCK_API) {
      await delay(200);
      const group = mockGroups.find(g => g.id === id);
      if (!group) {
        throw new Error(`Group with ID ${id} not found`);
      }
      return group;
    }
    
    // Use real API
    try {
      return await apiService.get<Group>(`/groups/${id}`);
    } catch (error) {
      console.error(`Error fetching group with ID ${id}:`, error);
      throw error;
    }
  },
  
  getGroupWords: async (groupId: string, page: number = 1, limit: number = 20): Promise<{words: Word[], total: number}> => {
    if (USE_MOCK_API) {
      await delay(300);
      // Filter mock words (in a real app, we'd have a proper relationship)
      const filteredWords = mockWords;
      
      // Paginate the results
      const start = (page - 1) * limit;
      const end = Math.min(start + limit, filteredWords.length);
      return {
        words: filteredWords.slice(start, end),
        total: filteredWords.length
      };
    }
    
    // Use real API
    try {
      const params = { page, limit };
      return await apiService.get<{words: Word[], total: number}>(`/groups/${groupId}/words`, params);
    } catch (error) {
      console.error(`Error fetching words for group ID ${groupId}:`, error);
      throw error;
    }
  },
  
  getGroupSessions: async (groupId: string, page: number = 1, limit: number = 10): Promise<{sessions: StudySession[], total: number}> => {
    if (USE_MOCK_API) {
      await delay(250);
      // Filter mock sessions for the specific group
      const filteredSessions = mockSessions.filter(s => s.group_id === groupId);
      
      // Paginate the results
      const start = (page - 1) * limit;
      const end = Math.min(start + limit, filteredSessions.length);
      return {
        sessions: filteredSessions.slice(start, end),
        total: filteredSessions.length
      };
    }
    
    // Use real API
    try {
      const params = { page, limit };
      return await apiService.get<{sessions: StudySession[], total: number}>(`/groups/${groupId}/study_sessions`, params);
    } catch (error) {
      console.error(`Error fetching study sessions for group ID ${groupId}:`, error);
      throw error;
    }
  },
  
  createGroup: async (groupData: CreateGroupRequest): Promise<Group> => {
    if (USE_MOCK_API) {
      await delay(350);
      // Create a new mock group
      const newGroup: Group = {
        id: (mockGroups.length + 1).toString(),
        name: groupData.name,
        word_count: 0
      };
      mockGroups.push(newGroup);
      return newGroup;
    }
    
    // Use real API
    try {
      return await apiService.post<Group>('/groups', groupData);
    } catch (error) {
      console.error('Error creating group:', error);
      throw error;
    }
  },
  
  clearCache: () => {
    cache.clearCache();
  },
  
  getWordsByGroupId: async (groupId: string): Promise<Word[]> => {
    if (USE_MOCK_API) {
      await delay(300);
      // Return all mock words for this group
      return mockWords;
    }
    
    // Use real API
    try {
      const response = await apiService.get<{words: Word[], total: number}>(`/groups/${groupId}/words`);
      return response.words;
    } catch (error) {
      console.error(`Error fetching words for group ID ${groupId}:`, error);
      throw error;
    }
  },
  
  getStudySessionsByGroupId: async (groupId: string): Promise<StudySession[]> => {
    if (USE_MOCK_API) {
      await delay(250);
      return mockSessions.filter(s => s.group_id === groupId);
    }
    
    try {
      const response = await apiService.get<{sessions: StudySession[], total: number}>(`/groups/${groupId}/study_sessions`);
      return response.sessions;
    } catch (error) {
      console.error(`Error fetching study sessions for group ID ${groupId}:`, error);
      throw error;
    }
  }
};

export default GroupService; 