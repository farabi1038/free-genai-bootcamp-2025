# API Integration Guide

This guide explains how to correctly integrate the frontend with the backend API in the Language Learning Portal application.

## Table of Contents

1. [API Client Setup](#api-client-setup)
2. [Error Handling](#error-handling)
3. [Loading States](#loading-states)
4. [Using the API Services](#using-the-api-services)
5. [The useApi Hook](#the-useapi-hook)
6. [CORS Configuration](#cors-configuration)
7. [Best Practices](#best-practices)

## API Client Setup

The application uses Axios for API calls, configured in `src/api/client.ts`. The base configuration includes:

```typescript
// Create axios instance with base URL and common settings
const apiClient = axios.create({
  baseURL: '/api',                  // Base URL for all API calls
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,                  // 10 seconds timeout
});
```

In development, Vite is configured to proxy API requests to the backend:

```javascript
// vite.config.js
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080', // The backend server URL
        changeOrigin: true
      }
    }
  }
});
```

## Error Handling

Error handling is implemented at multiple levels:

1. **Global Error Context**: The `ErrorContext` provides a way to display error messages across the application.
2. **API Client Error Interceptor**: The Axios interceptor standardizes error responses.
3. **Component-Level Error Handling**: Components can handle errors specific to their needs.

### Error Response Format

```typescript
interface ApiErrorResponse {
  success: false;
  error: {
    message: string;
    status: number;
    details?: any;
  };
}
```

### Using the Error Context

```typescript
import { useError } from '../contexts/ErrorContext';

const MyComponent = () => {
  const { setError } = useError();
  
  const handleError = (error) => {
    setError({
      message: error.message,
      status: error.status || 500,
    });
  };
  
  // Use the handleError function when catching errors
};
```

## Loading States

Loading states are handled through:

1. **Global Loading Indicator**: The API client adds an `api-loading` class to the body when requests are in progress.
2. **Component-Level Loading States**: Components track loading state for specific requests.

### Using the LoadingIndicator

The `LoadingIndicator` component is automatically added to the `App` component and monitors the `api-loading` class on the body element.

## Using the API Services

The application has several service modules for API calls:

- `wordService.ts`: For word-related endpoints
- `groupService.ts`: For group-related endpoints
- `studyActivityService.ts`: For study activity endpoints

Each service uses the `apiService` methods for consistent error handling:

```typescript
const WordService = {
  getAllWords: async (): Promise<Word[]> => {
    return apiService.get<Word[]>('/words');
  },
  
  getWordById: async (id: string): Promise<Word> => {
    return apiService.get<Word>(`/words/${id}`);
  },
  
  // More methods...
};
```

## The useApi Hook

The `useApi` hook provides a standardized way to handle API calls, loading states, and errors:

```typescript
const { data, loading, error, execute } = useApi(WordService.getAllWords);

// Call the API
useEffect(() => {
  execute();
}, [execute]);

// Show loading state
{loading && <p>Loading...</p>}

// Handle error state
{error && <p>Error: {error.message}</p>}

// Use data
{data && data.map(item => (
  <div key={item.id}>{item.name}</div>
))}
```

## CORS Configuration

The backend should be configured to allow requests from the frontend domain. In development, the Vite proxy handles this for you. In production, either configure CORS on the backend or serve both frontend and backend from the same domain.

## Best Practices

1. **Use Typed Responses**: Always use TypeScript interfaces for API responses.
2. **Consistent Error Handling**: Use the `useApi` hook for consistent error handling.
3. **Retry Logic**: The API client includes retry logic for certain types of errors.
4. **Cache Where Appropriate**: Consider using React Query for caching frequently accessed data.
5. **Lazy Loading**: Load data only when needed to improve performance.
6. **Input Validation**: Validate inputs before sending them to the API.
7. **Manage Loading States**: Always show loading indicators for better user experience.
8. **KISS (Keep It Simple, Stupid)**: Don't over-engineer API calls. Stick to the patterns established in the codebase.

## Example Implementation

```typescript
import React, { useEffect } from 'react';
import useApi from '../../hooks/useApi';
import WordService from '../../api/wordService';

const WordsList = () => {
  const { data: words, loading, error, execute } = useApi(WordService.getAllWords);

  useEffect(() => {
    execute();
  }, [execute]);

  if (loading) return <div className="spinner" />;
  if (error) return <div className="error">Error: {error.message}</div>;
  if (!words || words.length === 0) return <div>No words found</div>;

  return (
    <div>
      <h1>Words</h1>
      <ul>
        {words.map(word => (
          <li key={word.id}>{word.japanese} - {word.english}</li>
        ))}
      </ul>
    </div>
  );
};

export default WordsList;
```

By following these guidelines, you'll ensure a consistent and robust integration between the frontend and backend of the Language Learning Portal application. 