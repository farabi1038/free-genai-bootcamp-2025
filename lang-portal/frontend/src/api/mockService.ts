import { LastStudySession, StudyProgress, QuickStats, StudyActivity, Group, Word, StudySession, StudySessionDetail, WordResult } from './types';

// Simulated network delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Mock data for dashboard
const mockLastStudySession: LastStudySession = {
  activity: 'Vocabulary Quiz',
  timestamp: new Date().toISOString(),
  correct: 15,
  wrong: 3,
  group: 'Basic Japanese',
  group_id: '1'
};

const mockStudyProgress: StudyProgress = {
  wordsStudied: 3,
  totalWords: 124,
  masteryRate: 2
};

const mockQuickStats: QuickStats = {
  successRate: 83,
  totalSessions: 4,
  activeGroups: 3,
  streak: 2
};

// Mock data for study activities
const mockStudyActivities: StudyActivity[] = [
  {
    id: '1',
    name: 'Vocabulary Flashcards',
    description: 'Practice vocabulary with digital flashcards. See the word in Japanese and try to recall the meaning.',
    thumbnail_url: 'https://placehold.co/600x400/88C0D0/ECEFF4?text=Flashcards',
    url: 'https://example.com/flashcards'
  },
  {
    id: '2',
    name: 'Word Quiz',
    description: 'Test your knowledge with a multiple-choice quiz on Japanese vocabulary.',
    thumbnail_url: 'https://placehold.co/600x400/A3BE8C/ECEFF4?text=Quiz',
    url: 'https://example.com/quiz'
  },
  {
    id: '3',
    name: 'Spelling Practice',
    description: 'Practice spelling Japanese words using romaji input.',
    thumbnail_url: 'https://placehold.co/600x400/B48EAD/ECEFF4?text=Spelling',
    url: 'https://example.com/spelling'
  },
  {
    id: '4',
    name: 'Listening Exercise',
    description: 'Listen to Japanese words and phrases and type what you hear.',
    thumbnail_url: 'https://placehold.co/600x400/EBCB8B/2E3440?text=Listening',
    url: 'https://example.com/listening'
  }
];

// Mock data for groups
const mockGroups: Group[] = [
  { id: '1', name: 'Basic Japanese', word_count: 52 },
  { id: '2', name: 'Food Words', word_count: 35 },
  { id: '3', name: 'Travel Words', word_count: 48 },
  { id: '4', name: 'JLPT N5 Vocabulary', word_count: 115 },
  { id: '5', name: 'Common Verbs', word_count: 78 },
  { id: '6', name: 'Adjectives', word_count: 43 },
  { id: '7', name: 'Family Terms', word_count: 24 },
  { id: '8', name: 'Time Expressions', word_count: 31 }
];

// Mock words for each group
const mockGroupWords: { [key: string]: Word[] } = {
  '1': [
    { id: '1', japanese: '犬', romaji: 'inu', english: 'dog', correct_count: 8, wrong_count: 2 },
    { id: '2', japanese: '猫', romaji: 'neko', english: 'cat', correct_count: 12, wrong_count: 1 },
    { id: '3', japanese: '魚', romaji: 'sakana', english: 'fish', correct_count: 5, wrong_count: 3 },
    { id: '4', japanese: '鳥', romaji: 'tori', english: 'bird', correct_count: 7, wrong_count: 0 },
    { id: '5', japanese: '水', romaji: 'mizu', english: 'water', correct_count: 10, wrong_count: 2 }
  ],
  '2': [
    { id: '11', japanese: 'ご飯', romaji: 'gohan', english: 'rice/meal', correct_count: 6, wrong_count: 2 },
    { id: '12', japanese: '肉', romaji: 'niku', english: 'meat', correct_count: 9, wrong_count: 1 },
    { id: '13', japanese: '野菜', romaji: 'yasai', english: 'vegetables', correct_count: 7, wrong_count: 3 },
    { id: '14', japanese: '果物', romaji: 'kudamono', english: 'fruit', correct_count: 5, wrong_count: 2 },
    { id: '15', japanese: '飲み物', romaji: 'nomimono', english: 'drink', correct_count: 8, wrong_count: 0 }
  ],
  // Add more mock words for other groups as needed
};

// Mock study sessions for each group
const mockGroupSessions: { [key: string]: StudySession[] } = {
  '1': [
    { 
      id: '101', 
      activity_id: '1',
      activity_name: 'Vocabulary Flashcards', 
      group_id: '1',
      group_name: 'Basic Japanese', 
      start_time: '2025-03-04T10:30:00', 
      end_time: '2025-03-04T10:45:00', 
      review_item_count: 15 
    },
    { 
      id: '105', 
      activity_id: '2',
      activity_name: 'Word Quiz', 
      group_id: '1',
      group_name: 'Basic Japanese', 
      start_time: '2025-03-02T09:15:00', 
      end_time: '2025-03-02T09:30:00', 
      review_item_count: 20 
    }
  ],
  '2': [
    { 
      id: '102', 
      activity_id: '1',
      activity_name: 'Vocabulary Flashcards', 
      group_id: '2',
      group_name: 'Food Words', 
      start_time: '2025-03-03T14:20:00', 
      end_time: '2025-03-03T14:30:00', 
      review_item_count: 10 
    }
  ],
  '3': [
    { 
      id: '103', 
      activity_id: '1',
      activity_name: 'Vocabulary Flashcards', 
      group_id: '3',
      group_name: 'Travel Words', 
      start_time: '2025-03-01T09:15:00', 
      end_time: '2025-03-01T09:35:00', 
      review_item_count: 20 
    }
  ]
  // Add more mock sessions for other groups as needed
};

// Mock Dashboard API service
export const mockDashboardService = {
  getLastStudySession: async (): Promise<LastStudySession> => {
    await delay(600); // Simulate network delay
    return mockLastStudySession;
  },
  
  getStudyProgress: async (): Promise<StudyProgress> => {
    await delay(800);
    return mockStudyProgress;
  },
  
  getQuickStats: async (): Promise<QuickStats> => {
    await delay(1000);
    return mockQuickStats;
  }
};

// Mock Study Activity API service
export const mockStudyActivityService = {
  getAllActivities: async (): Promise<StudyActivity[]> => {
    await delay(800);
    return mockStudyActivities;
  },
  
  getActivityById: async (id: string): Promise<StudyActivity> => {
    await delay(500);
    const activity = mockStudyActivities.find(act => act.id === id);
    if (!activity) {
      throw new Error('Activity not found');
    }
    return activity;
  },
  
  launchActivity: async (activityId: string, groupId: string): Promise<any> => {
    await delay(300);
    // This would typically return a study session ID
    return {
      success: true,
      study_session_id: Math.floor(Math.random() * 10000)
    };
  }
};

// Mock Group API service
export const mockGroupService = {
  getAllGroups: async (): Promise<Group[]> => {
    await delay(200);
    return mockGroups;
  },
  
  getGroupById: async (id: string): Promise<Group> => {
    await delay(100);
    const group = mockGroups.find(g => g.id === id);
    if (!group) {
      throw new Error('Group not found');
    }
    return group;
  },
  
  getWordsByGroupId: async (id: string): Promise<Word[]> => {
    await delay(200);
    return mockGroupWords[id] || [];
  },
  
  getStudySessionsByGroupId: async (id: string): Promise<StudySession[]> => {
    await delay(150);
    return mockGroupSessions[id] || [];
  }
};

// Generate a larger set of mock words for pagination testing
const generateMockWords = (count: number): Word[] => {
  const words: Word[] = [];
  
  for (let i = 1; i <= count; i++) {
    words.push({
      id: `word${i}`,
      japanese: `単語${i}`,
      romaji: `tango${i}`,
      english: `Word ${i}`,
      correct_count: Math.floor(Math.random() * 10),
      wrong_count: Math.floor(Math.random() * 5),
      groups: [`group${(i % 5) + 1}`]
    });
  }
  
  return words;
};

// Generate 300 mock words
const allMockWords = generateMockWords(300);

// Add this to your mockService object
export const mockWordService = {
  getAllWords: async (page: number = 1, limit: number = 100): Promise<{words: Word[], total: number}> => {
    await delay(500);
    
    const start = (page - 1) * limit;
    const end = start + limit;
    const paginatedWords = allMockWords.slice(start, end);
    
    return {
      words: paginatedWords,
      total: allMockWords.length
    };
  },
  
  getWordById: async (id: string): Promise<Word> => {
    await delay(200);
    
    const word = allMockWords.find(w => w.id === id);
    if (!word) {
      throw new Error(`Word with id ${id} not found`);
    }
    
    return word;
  },
  
  createWord: async (wordData: any): Promise<Word> => {
    await delay(300);
    
    const newWord: Word = {
      id: `word-${allMockWords.length + 1}`,
      japanese: wordData.japanese,
      romaji: wordData.romaji,
      english: wordData.english,
      correct_count: 0,
      wrong_count: 0,
      groups: wordData.groups || []
    };
    
    // In a real implementation, we would add the word to the list
    // allMockWords.push(newWord);
    
    return newWord;
  }
};

// Generate mock study sessions
const mockStudySessions: StudySession[] = Array.from({ length: 50 }, (_, i) => {
  const startTime = new Date();
  startTime.setDate(startTime.getDate() - Math.floor(Math.random() * 30));
  
  const endTime = new Date(startTime);
  endTime.setMinutes(endTime.getMinutes() + Math.floor(Math.random() * 30) + 5);
  
  const reviewItemCount = Math.floor(Math.random() * 15) + 5;
  const correctCount = Math.floor(Math.random() * reviewItemCount);
  const wrongCount = reviewItemCount - correctCount;
  
  const activityTypes = ['Flashcards', 'Multiple Choice', 'Typing Practice', 'Matching Game'];
  
  return {
    id: `session-${i + 1}`,
    activity_name: activityTypes[Math.floor(Math.random() * activityTypes.length)],
    group_id: `group-${Math.floor(Math.random() * 10) + 1}`,
    group_name: `Group ${Math.floor(Math.random() * 10) + 1}`,
    start_time: startTime.toISOString(),
    end_time: endTime.toISOString(),
    review_item_count: reviewItemCount,
    correct_count: correctCount,
    wrong_count: wrongCount
  };
});

// Add study session methods to the mockService
const mockService = {
  getAllStudySessions: async (page: number = 1, limit: number = 10): Promise<{sessions: StudySession[], total: number}> => {
    await delay();
    const start = (page - 1) * limit;
    const end = start + limit;
    return {
      sessions: mockStudySessions.slice(start, end),
      total: mockStudySessions.length
    };
  },
  
  getStudySessionById: async (id: string): Promise<StudySessionDetail> => {
    await delay();
    const session = mockStudySessions.find(session => session.id === id);
    
    if (!session) {
      throw new Error(`Study session with ID ${id} not found`);
    }
    
    // Generate mock word results for this session
    const wordResults: WordResult[] = Array.from({ length: session.review_item_count }, (_, i) => {
      const isCorrect = i < session.correct_count;
      return {
        word_id: `word-${Math.floor(Math.random() * 300) + 1}`,
        japanese: `単語${i + 1}`,
        romaji: `tango${i + 1}`,
        english: `word${i + 1}`,
        is_correct: isCorrect,
        response_time_ms: Math.floor(Math.random() * 5000) + 1000
      };
    });
    
    const totalResponseTime = wordResults.reduce((sum, result) => sum + result.response_time_ms, 0);
    
    return {
      ...session,
      word_results: wordResults,
      accuracy_percentage: (session.correct_count / session.review_item_count) * 100,
      average_response_time_ms: totalResponseTime / session.review_item_count
    };
  }
};

export default mockService; 