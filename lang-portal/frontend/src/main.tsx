import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { ErrorProvider } from './contexts/ErrorContext'

// Ensure favicon is accessible
const link = document.createElement('link');
link.rel = 'icon';
link.href = '/favicon.svg';
document.head.appendChild(link);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorProvider>
      <App />
    </ErrorProvider>
  </StrictMode>,
)
