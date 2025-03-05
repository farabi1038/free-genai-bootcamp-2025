import { delay } from './utils';
import apiService from './apiService';

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

// Set to false to use the real API
const USE_MOCK_API = false;

const LOCAL_STORAGE_THEME_KEY = 'lang_portal_theme';

const getSettingsService = () => {
  return {
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
        const response = await apiService.get<UserSettings>('/settings');
        return response;
      } catch (error) {
        console.error('Error fetching user settings:', error);
        // Fall back to localStorage if API fails
        const savedSettings = localStorage.getItem('userSettings');
        if (savedSettings) {
          return JSON.parse(savedSettings);
        }
        return defaultSettings;
      }
    },

    saveUserSettings: async (settings: UserSettings): Promise<void> => {
      if (USE_MOCK_API) {
        await delay(500);
        localStorage.setItem('userSettings', JSON.stringify(settings));
        return;
      }

      try {
        await apiService.post('/settings', settings);
        // Still save to localStorage as a backup
        localStorage.setItem('userSettings', JSON.stringify(settings));
      } catch (error) {
        console.error('Error saving user settings:', error);
        // At least save to localStorage if API fails
        localStorage.setItem('userSettings', JSON.stringify(settings));
        throw error;
      }
    },

    resetStudyHistory: async (): Promise<void> => {
      if (USE_MOCK_API) {
        await delay(1000);
        console.log('Mock API: Study history reset');
        return;
      }

      try {
        await apiService.post('/reset_history', {});
      } catch (error) {
        console.error('Error resetting study history:', error);
        throw error;
      }
    },

    performFullReset: async (): Promise<void> => {
      if (USE_MOCK_API) {
        await delay(1500);
        localStorage.removeItem('userSettings');
        console.log('Mock API: Full reset performed');
        return;
      }

      try {
        await apiService.post('/full_reset', {});
        // Clear localStorage
        localStorage.removeItem('userSettings');
      } catch (error) {
        console.error('Error performing full reset:', error);
        throw error;
      }
    },
    
    // Theme handling utility
    setTheme: (theme: 'light' | 'dark' | 'system'): void => {
      localStorage.setItem(LOCAL_STORAGE_THEME_KEY, theme);
      
      if (theme === 'system') {
        // Check system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
      } else {
        // Set specific theme
        document.documentElement.setAttribute('data-theme', theme);
      }
    }
  };
};

const settingsService = getSettingsService();
export default settingsService; 