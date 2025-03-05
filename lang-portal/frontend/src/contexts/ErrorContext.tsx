import { createContext, useContext, ReactNode, useState } from 'react';

interface ErrorContextType {
  error: ErrorState | null;
  setError: (error: ErrorState | null) => void;
  clearError: () => void;
}

interface ErrorState {
  message: string;
  status?: number;
}

const ErrorContext = createContext<ErrorContextType | undefined>(undefined);

export function ErrorProvider({ children }: { children: ReactNode }) {
  const [error, setError] = useState<ErrorState | null>(null);

  const clearError = () => setError(null);

  return (
    <ErrorContext.Provider value={{ error, setError, clearError }}>
      {children}
    </ErrorContext.Provider>
  );
}

export function useError() {
  const context = useContext(ErrorContext);
  if (context === undefined) {
    throw new Error('useError must be used within an ErrorProvider');
  }
  return context;
} 