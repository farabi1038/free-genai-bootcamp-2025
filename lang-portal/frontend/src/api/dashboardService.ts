import { format } from 'date-fns';
import { 
  LastStudySession as ExistingLastStudySession, 
  StudyProgress as ExistingStudyProgress, 
  QuickStats as ExistingQuickStats,
  Word,
  Group
} from './types';

// Create a function to generate mock data for testing
const generateMockWords = (count: number): Word[] => {
  const words: Word[] = [];
  
  for (let i = 0; i < count; i++) {
    words.push({
      id: `word-${i + 1}`,
      japanese: `単語${i + 1}`,
      romaji: `tango${i + 1}`,
      english: `Word ${i + 1}`,
      correct_count: Math.floor(Math.random() * 10),
      wrong_count: Math.floor(Math.random() * 5)
    });
  }
  
  return words;
};

const generateMockGroups = (count: number): Group[] => {
  const groups: Group[] = [];
  
  for (let i = 0; i < count; i++) {
    groups.push({
      id: `group-${i + 1}`,
      name: `Group ${i + 1}`,
      word_count: Math.floor(Math.random() * 30) + 10
    });
  }
  
  return groups;
};

// Generate mock data
const mockWords = generateMockWords(100);
const mockGroups = generateMockGroups(8);

// Dashboard Service
const DashboardService = {
  getLastStudySession: async (): Promise<ExistingLastStudySession | null> => {
    await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API delay
    
    // 10% chance of no last session
    if (Math.random() > 0.9) {
      return null;
    }
    
    const randomGroup = mockGroups[Math.floor(Math.random() * mockGroups.length)];
    
    return {
      activity: ['Flashcards', 'Multiple Choice', 'Typing Practice', 'Matching Game'][Math.floor(Math.random() * 4)],
      timestamp: format(new Date(Date.now() - Math.random() * 86400000 * 3), "yyyy-MM-dd'T'HH:mm:ss"),
      correct: Math.floor(Math.random() * 15) + 5,
      wrong: Math.floor(Math.random() * 10),
      group: randomGroup.name,
      group_id: randomGroup.id
    };
  },
  
  getStudyProgress: async (): Promise<ExistingStudyProgress> => {
    await new Promise(resolve => setTimeout(resolve, 700)); // Simulate API delay
    
    return {
      wordsStudied: Math.floor(Math.random() * 150) + 50,
      totalWords: mockWords.length,
      masteryRate: Math.floor(Math.random() * 45) + 55
    };
  },
  
  getQuickStats: async (): Promise<ExistingQuickStats> => {
    await new Promise(resolve => setTimeout(resolve, 600)); // Simulate API delay
    
    return {
      successRate: Math.floor(Math.random() * 30) + 70,
      totalSessions: Math.floor(Math.random() * 50) + 10,
      activeGroups: mockGroups.length,
      streak: Math.floor(Math.random() * 10) + 1
    };
  }
};

export default DashboardService; 