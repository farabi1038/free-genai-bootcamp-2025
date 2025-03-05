import { useState } from 'react'
import Layout from './components/Layout'
import Dashboard from './components/Dashboard'
import PlaceholderPage from './components/PlaceholderPage'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')

  // Function to handle navigation between pages
  const handleNavigate = (page: string) => {
    setCurrentPage(page)
  }

  // Render the appropriate content based on the current page
  const renderContent = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />
      case 'study':
        return <PlaceholderPage title="Study Activities" description="Browse and launch your language learning activities." />
      case 'words':
        return <PlaceholderPage title="Words" description="View and manage your vocabulary words." />
      case 'groups':
        return <PlaceholderPage title="Word Groups" description="Organize your vocabulary into thematic groups." />
      case 'sessions':
        return <PlaceholderPage title="Study Sessions" description="Review your past learning sessions and track progress." />
      case 'settings':
        return <PlaceholderPage title="Settings" description="Configure your application preferences." />
      default:
        return <Dashboard />
    }
  }

  return (
    <Layout onNavigate={handleNavigate} currentPage={currentPage}>
      {renderContent()}
    </Layout>
  )
}

export default App
