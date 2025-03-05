import React, { createContext, useState, useEffect, useContext, ReactNode } from 'react';
import settingsService, { UserSettings } from '../api/settingsService';

interface SettingsContextType {
  settings: UserSettings | null;
  loading: boolean;
  error: Error | null;
  updateSettings: (newSettings: UserSettings) => Promise<void>;
  resetSettings: () => Promise<void>;
}

const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};

interface SettingsProviderProps {
  children: ReactNode;
}

export const SettingsProvider: React.FC<SettingsProviderProps> = ({ children }) => {
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  // Fetch settings on component mount
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        const data = await settingsService.getUserSettings();
        setSettings(data);
        setError(null);
      } catch (err) {
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, []);

  // Update settings
  const updateSettings = async (newSettings: UserSettings) => {
    try {
      setLoading(true);
      const updatedSettings = await settingsService.updateUserSettings(newSettings);
      setSettings(updatedSettings);
      setError(null);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  // Reset settings to defaults
  const resetSettings = async () => {
    try {
      setLoading(true);
      const defaultSettings = await settingsService.resetUserSettings();
      setSettings(defaultSettings);
      setError(null);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SettingsContext.Provider
      value={{
        settings,
        loading,
        error,
        updateSettings,
        resetSettings,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
}; 