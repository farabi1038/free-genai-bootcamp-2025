import { ActivityType } from './types';
import { delay } from './utils';

const USE_MOCK_API = true;

// Activity descriptions and details
const mockActivities: ActivityType[] = [
  {
    id: 'flashcards',
    name: 'Flashcards',
    description: 'Review vocabulary cards with Japanese on one side and English on the other.',
    icon: 'card',
    benefits: [
      'Build recognition memory',
      'Quick reviews of many words',
      'Test your recall in both directions'
    ],
    recommendedFor: 'Quick daily vocabulary review',
    difficulty: 'beginner',
    instructions: 'Tap a card to flip between Japanese and English. Mark each word as correct or incorrect to track your progress.'
  },
  {
    id: 'multiple-choice',
    name: 'Multiple Choice',
    description: 'Choose the correct translation from four options.',
    icon: 'list',
    benefits: [
      'Strengthen word recognition',
      'Practice choosing between similar words',
      'Less pressure than recall-based activities'
    ],
    recommendedFor: 'Building confidence with new vocabulary',
    difficulty: 'beginner',
    instructions: 'Read the word at the top, then select the correct translation from the four options below.'
  },
  {
    id: 'typing',
    name: 'Typing Practice',
    description: 'Type the correct translation to improve spelling and active recall.',
    icon: 'keyboard',
    benefits: [
      'Strengthens active recall',
      'Improves spelling accuracy',
      'Builds writing confidence'
    ],
    recommendedFor: 'Mastering vocabulary you already recognize',
    difficulty: 'intermediate',
    instructions: 'Type the correct translation in the text field. Your answer will be checked for accuracy.'
  },
  {
    id: 'matching',
    name: 'Matching Game',
    description: 'Match pairs of words in a memory-style game.',
    icon: 'grid',
    benefits: [
      'Makes learning fun and engaging',
      'Builds visual-spatial memory',
      'Helps associate words with their translations'
    ],
    recommendedFor: 'Fun, game-based learning sessions',
    difficulty: 'beginner',
    instructions: 'Click cards to reveal words, and find matching Japanese-English pairs. The game ends when all pairs are matched.'
  }
];

const ActivitiesService = {
  getAllActivities: async (): Promise<ActivityType[]> => {
    if (USE_MOCK_API) {
      await delay(600);
      return mockActivities;
    }

    try {
      const response = await fetch('/api/activities');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching activities:', error);
      throw error;
    }
  },

  getActivityById: async (id: string): Promise<ActivityType> => {
    if (USE_MOCK_API) {
      await delay(400);
      const activity = mockActivities.find(activity => activity.id === id);
      if (!activity) {
        throw new Error(`Activity with ID ${id} not found`);
      }
      return activity;
    }

    try {
      const response = await fetch(`/api/activities/${id}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching activity details:', error);
      throw error;
    }
  }
};

export default ActivitiesService; 