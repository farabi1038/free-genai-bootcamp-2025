import { delay } from './utils';

export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  wordsPerStudySession: number;
  showRomaji: boolean;
  defaultStudyActivity: string;
  notifications: boolean;
  audioEnabled: boolean;
  showEnglishFirst: boolean;
  autoAdvanceTimeout: number; // in seconds
}

const defaultSettings: UserSettings = {
  theme: 'system',
  wordsPerStudySession: 20,
  showRomaji: true,
  defaultStudyActivity: 'flashcards',
  notifications: true,
  audioEnabled: true,
  showEnglishFirst: false,
  autoAdvanceTimeout: 5
};

const USE_MOCK_API = true;

const SettingsService = {
  getUserSettings: async (): Promise<UserSettings> => {
    if (USE_MOCK_API) {
      await delay(500);
      // Try to get from localStorage first
      const savedSettings = localStorage.getItem('userSettings');
      if (savedSettings) {
        return JSON.parse(savedSettings);
      }
      // Otherwise return defaults
      return defaultSettings;
    }

    try {
      const response = await fetch('/api/settings');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching user settings:', error);
      throw error;
    }
  },

  updateUserSettings: async (settings: UserSettings): Promise<UserSettings> => {
    if (USE_MOCK_API) {
      await delay(700);
      // Save to localStorage for persistence
      localStorage.setItem('userSettings', JSON.stringify(settings));
      return settings;
    }

    try {
      const response = await fetch('/api/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error updating user settings:', error);
      throw error;
    }
  },

  resetUserSettings: async (): Promise<UserSettings> => {
    if (USE_MOCK_API) {
      await delay(600);
      // Remove from localStorage and return defaults
      localStorage.removeItem('userSettings');
      return defaultSettings;
    }

    try {
      const response = await fetch('/api/settings/reset', {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error resetting user settings:', error);
      throw error;
    }
  }
};

export default SettingsService; 