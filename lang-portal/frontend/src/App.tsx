import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/layout/Navbar'
import NotFound from './components/layout/NotFound'
import ActivitySelectorPage from './components/study/ActivitySelectorPage'
import StudyPage from './components/study/StudyPage'
import WordsPage from './components/words/WordsPage'
import WordDetails from './components/words/WordDetails'
import GroupsPage from './components/groups/GroupsPage'
import GroupDetails from './components/groups/GroupDetails'
import SessionsPage from './components/sessions/SessionsPage'
import SessionDetails from './components/sessions/SessionDetails'
import { SettingsProvider } from './contexts/SettingsContext'
import SettingsPage from './components/settings/SettingsPage'
import { SearchProvider } from './contexts/SearchContext'
import DashboardPage from './components/dashboard/DashboardPage'
import { ThemeProvider } from 'styled-components'
import { theme } from './styles/theme'
import GlobalStyle from './styles/GlobalStyle'

function App() {
  return (
    <SearchProvider>
      <SettingsProvider>
        <ThemeProvider theme={theme}>
          <GlobalStyle />
          <Router>
            <Navbar />
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/study" element={<ActivitySelectorPage />} />
              <Route path="/study/:activityType" element={<StudyPage />} />
              <Route path="/study/:activityType/:groupId" element={<StudyPage />} />
              <Route path="/words" element={<WordsPage />} />
              <Route path="/words/:id" element={<WordDetails />} />
              <Route path="/groups" element={<GroupsPage />} />
              <Route path="/groups/:id" element={<GroupDetails />} />
              <Route path="/sessions" element={<SessionsPage />} />
              <Route path="/sessions/:id" element={<SessionDetails />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Router>
        </ThemeProvider>
      </SettingsProvider>
    </SearchProvider>
  )
}

export default App
