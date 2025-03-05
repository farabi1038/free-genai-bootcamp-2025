import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { theme } from '../../styles/theme';
import { useSettings } from '../../contexts/SettingsContext';
import LoadingIndicator from '../ui/LoadingIndicator';

const Container = styled.div`
  padding: ${theme.spacing.lg};
  max-width: 800px;
  margin: 0 auto;
`;

const Header = styled.div`
  margin-bottom: ${theme.spacing.lg};
`;

const Title = styled.h1`
  color: ${theme.colors.textDark};
  margin: 0 0 ${theme.spacing.sm} 0;
`;

const Description = styled.p`
  color: ${theme.colors.textLight};
  margin: 0;
`;

const SettingsCard = styled.div`
  background-color: ${theme.colors.snow0};
  border-radius: ${theme.borderRadius};
  padding: ${theme.spacing.lg};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: ${theme.spacing.lg};
`;

const SettingGroup = styled.div`
  margin-bottom: ${theme.spacing.lg};
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const SettingGroupTitle = styled.h2`
  color: ${theme.colors.frost3};
  margin: 0 0 ${theme.spacing.md} 0;
  font-size: 1.2rem;
  padding-bottom: ${theme.spacing.sm};
  border-bottom: 1px solid ${theme.colors.snow1};
`;

const Setting = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${theme.spacing.md} 0;
  border-bottom: 1px solid ${theme.colors.snow1};
  
  &:last-child {
    border-bottom: none;
  }
`;

const SettingLabel = styled.div`
  display: flex;
  flex-direction: column;
`;

const Label = styled.label`
  font-weight: bold;
  color: ${theme.colors.textDark};
  margin-bottom: ${theme.spacing.xs};
`;

const Description2 = styled.span`
  font-size: 0.9rem;
  color: ${theme.colors.textLight};
`;

const Select = styled.select`
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  border: 1px solid ${theme.colors.snow3};
  background-color: white;
  min-width: 150px;
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.frost2};
    box-shadow: 0 0 0 2px rgba(94, 129, 172, 0.2);
  }
`;

const Input = styled.input`
  padding: ${theme.spacing.sm} ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  border: 1px solid ${theme.colors.snow3};
  background-color: white;
  width: 80px;
  
  &:focus {
    outline: none;
    border-color: ${theme.colors.frost2};
    box-shadow: 0 0 0 2px rgba(94, 129, 172, 0.2);
  }
  
  &[type="checkbox"] {
    width: auto;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: ${theme.spacing.md};
  margin-top: ${theme.spacing.lg};
`;

const Button = styled.button`
  padding: ${theme.spacing.sm} ${theme.spacing.lg};
  border-radius: ${theme.borderRadius};
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
`;

const PrimaryButton = styled(Button)`
  background-color: ${theme.colors.frost3};
  color: white;
  border: none;
  
  &:hover {
    background-color: ${theme.colors.frost2};
  }
  
  &:disabled {
    background-color: ${theme.colors.disabled};
    cursor: not-allowed;
  }
`;

const SecondaryButton = styled(Button)`
  background-color: transparent;
  color: ${theme.colors.frost3};
  border: 1px solid ${theme.colors.frost3};
  
  &:hover {
    background-color: ${theme.colors.snow1};
  }
`;

const ErrorMessage = styled.div`
  background-color: ${theme.colors.aurora0};
  color: white;
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  margin-bottom: ${theme.spacing.md};
`;

const SuccessMessage = styled.div`
  background-color: ${theme.colors.aurora4};
  color: white;
  padding: ${theme.spacing.md};
  border-radius: ${theme.borderRadius};
  margin-bottom: ${theme.spacing.md};
`;

const SettingsPage: React.FC = () => {
  const { settings, loading, error, updateSettings, resetSettings } = useSettings();
  const [localSettings, setLocalSettings] = useState(settings);
  const [hasChanges, setHasChanges] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');
  
  // Update local settings when settings from context change
  useEffect(() => {
    if (settings) {
      setLocalSettings(settings);
    }
  }, [settings]);
  
  // Detect changes between local and context settings
  useEffect(() => {
    if (settings && localSettings) {
      const isChanged = JSON.stringify(settings) !== JSON.stringify(localSettings);
      setHasChanges(isChanged);
    }
  }, [settings, localSettings]);
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target as HTMLInputElement;
    
    setLocalSettings(prev => {
      if (!prev) return prev;
      
      if (type === 'checkbox') {
        const target = e.target as HTMLInputElement;
        return { ...prev, [name]: target.checked };
      }
      
      if (type === 'number') {
        return { ...prev, [name]: parseInt(value) };
      }
      
      return { ...prev, [name]: value };
    });
  };
  
  const handleSave = async () => {
    if (!localSettings) return;
    
    try {
      setSaveStatus('saving');
      await updateSettings(localSettings);
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (err) {
      setSaveStatus('error');
    }
  };
  
  const handleReset = async () => {
    try {
      setSaveStatus('saving');
      await resetSettings();
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (err) {
      setSaveStatus('error');
    }
  };
  
  if (loading && !settings) {
    return (
      <Container>
        <LoadingIndicator text="Loading settings..." />
      </Container>
    );
  }
  
  if (error) {
    return (
      <Container>
        <ErrorMessage>
          Error loading settings: {error.message}
        </ErrorMessage>
      </Container>
    );
  }
  
  if (!localSettings) {
    return (
      <Container>
        <ErrorMessage>
          Settings could not be loaded. Please try again.
        </ErrorMessage>
      </Container>
    );
  }
  
  return (
    <Container>
      <Header>
        <Title>Settings</Title>
        <Description>Configure your learning experience preferences</Description>
      </Header>
      
      {saveStatus === 'success' && (
        <SuccessMessage>
          Settings saved successfully!
        </SuccessMessage>
      )}
      
      {saveStatus === 'error' && (
        <ErrorMessage>
          Error saving settings. Please try again.
        </ErrorMessage>
      )}
      
      <SettingsCard>
        <SettingGroup>
          <SettingGroupTitle>Appearance</SettingGroupTitle>
          
          <Setting>
            <SettingLabel>
              <Label htmlFor="theme">Theme</Label>
              <Description2>Choose your preferred color theme</Description2>
            </SettingLabel>
            <Select
              id="theme"
              name="theme"
              value={localSettings.theme}
              onChange={handleInputChange}
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="system">System (Auto)</option>
            </Select>
          </Setting>
        </SettingGroup>
        
        <SettingGroup>
          <SettingGroupTitle>Study Preferences</SettingGroupTitle>
          
          <Setting>
            <SettingLabel>
              <Label htmlFor="wordsPerStudySession">Words Per Study Session</Label>
              <Description2>Number of words in each study session</Description2>
            </SettingLabel>
            <Input
              id="wordsPerStudySession"
              name="wordsPerStudySession"
              type="number"
              min="5"
              max="50"
              value={localSettings.wordsPerStudySession}
              onChange={handleInputChange}
            />
          </Setting>
          
          <Setting>
            <SettingLabel>
              <Label htmlFor="showRomaji">Show Romaji</Label>
              <Description2>Display romanized pronunciation</Description2>
            </SettingLabel>
            <Input
              id="showRomaji"
              name="showRomaji"
              type="checkbox"
              checked={localSettings.showRomaji}
              onChange={handleInputChange}
            />
          </Setting>
          
          <Setting>
            <SettingLabel>
              <Label htmlFor="showEnglishFirst">Show English First</Label>
              <Description2>Show English translation before Japanese</Description2>
            </SettingLabel>
            <Input
              id="showEnglishFirst"
              name="showEnglishFirst"
              type="checkbox"
              checked={localSettings.showEnglishFirst}
              onChange={handleInputChange}
            />
          </Setting>
          
          <Setting>
            <SettingLabel>
              <Label htmlFor="defaultStudyActivity">Default Study Activity</Label>
              <Description2>Choose your preferred study activity</Description2>
            </SettingLabel>
            <Select
              id="defaultStudyActivity"
              name="defaultStudyActivity"
              value={localSettings.defaultStudyActivity}
              onChange={handleInputChange}
            >
              <option value="flashcards">Flashcards</option>
              <option value="multiple-choice">Multiple Choice</option>
              <option value="typing">Typing Practice</option>
              <option value="matching">Matching Game</option>
            </Select>
          </Setting>
          
          <Setting>
            <SettingLabel>
              <Label htmlFor="autoAdvanceTimeout">Auto Advance Timeout (seconds)</Label>
              <Description2>Time before automatically advancing to next card (0 to disable)</Description2>
            </SettingLabel>
            <Input
              id="autoAdvanceTimeout"
              name="autoAdvanceTimeout"
              type="number"
              min="0"
              max="20"
              value={localSettings.autoAdvanceTimeout}
              onChange={handleInputChange}
            />
          </Setting>
        </SettingGroup>
        
        <SettingGroup>
          <SettingGroupTitle>Notifications & Sound</SettingGroupTitle>
          
          <Setting>
            <SettingLabel>
              <Label htmlFor="notifications">Enable Notifications</Label>
              <Description2>Receive study reminders and updates</Description2>
            </SettingLabel>
            <Input
              id="notifications"
              name="notifications"
              type="checkbox"
              checked={localSettings.notifications}
              onChange={handleInputChange}
            />
          </Setting>
          
          <Setting>
            <SettingLabel>
              <Label htmlFor="audioEnabled">Enable Audio</Label>
              <Description2>Play pronunciation and feedback sounds</Description2>
            </SettingLabel>
            <Input
              id="audioEnabled"
              name="audioEnabled"
              type="checkbox"
              checked={localSettings.audioEnabled}
              onChange={handleInputChange}
            />
          </Setting>
        </SettingGroup>
      </SettingsCard>
      
      <ButtonGroup>
        <SecondaryButton onClick={handleReset}>
          Reset to Defaults
        </SecondaryButton>
        <PrimaryButton 
          onClick={handleSave} 
          disabled={!hasChanges || saveStatus === 'saving'}
        >
          {saveStatus === 'saving' ? 'Saving...' : 'Save Changes'}
        </PrimaryButton>
      </ButtonGroup>
    </Container>
  );
};

export default SettingsPage; 