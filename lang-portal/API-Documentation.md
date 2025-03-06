# Language Learning Portal API Documentation

This document provides a comprehensive guide to the Language Learning Portal API, clearly separating frontend and backend responsibilities.

## API Endpoints

### 1. Dashboard APIs

#### GET /api/dashboard/last_study_session
- **Purpose**: Retrieve the most recent study session
- **Backend Responsibility**: 
  - Query the database for the most recent study session
  - Include group details
  - Format with dates in ISO format
- **Frontend Responsibility**:
  - Display session details on the dashboard
  - Handle empty response (no sessions yet)
  - Format date for user display

**Response Format**:
```json
{
  "id": 123,
  "group_id": 456,
  "group_name": "Basic Greetings",
  "date": "2025-02-08T17:20:23-05:00",
  "score": 8,
  "total": 10
}
```

#### GET /api/dashboard/study_progress
- **Purpose**: Get the user's study progress statistics
- **Backend Responsibility**:
  - Calculate total available words
  - Calculate words studied and mastered
  - Calculate completion percentage
- **Frontend Responsibility**:
  - Display progress statistics
  - Render visual progress indicators

**Response Format**:
```json
{
  "total_words": 200,
  "words_studied": 85,
  "words_mastered": 42,
  "completion_rate": 21
}
```

#### GET /api/dashboard/quick_stats
- **Purpose**: Retrieve quick statistics for the dashboard
- **Backend Responsibility**:
  - Calculate statistics across groups, words, and sessions
  - Include average scores
- **Frontend Responsibility**:
  - Display statistics in dashboard widgets
  - Update dynamically when data changes

**Response Format**:
```json
{
  "total_groups": 5,
  "total_words": 200,
  "total_sessions": 15,
  "average_score": 76
}
```

### 2. Study Activities APIs

#### GET /api/study_activities
- **Purpose**: List all available study activities
- **Backend Responsibility**:
  - Return all study activities with their details
  - Include thumbnail URLs
- **Frontend Responsibility**:
  - Display activities in a grid or list
  - Include thumbnails and links

**Response Format**:
```json
[
  {
    "id": 1,
    "name": "Flashcards",
    "description": "Study vocabulary with flashcards",
    "thumbnail_url": "/images/flashcards.jpg",
    "url": "/study/flashcards",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
]
```

#### GET /api/study_activities/:id
- **Purpose**: Get details for a specific study activity
- **Backend Responsibility**:
  - Return detailed information for a study activity
- **Frontend Responsibility**:
  - Display activity details
  - Show options to launch the activity

**Response Format**:
```json
{
  "id": 1,
  "name": "Flashcards",
  "description": "Study vocabulary with flashcards",
  "thumbnail_url": "/images/flashcards.jpg",
  "url": "/study/flashcards",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### GET /api/study_activities/:id/study_sessions
- **Purpose**: Get study sessions for a specific activity
- **Backend Responsibility**:
  - Return sessions associated with the activity
  - Include group information
- **Frontend Responsibility**:
  - Display session history for the activity
  - Allow navigation to session details

**Response Format**:
```json
[
  {
    "id": 1,
    "group_id": 1,
    "group_name": "Basic Phrases",
    "activity_id": 1,
    "activity_name": "Flashcards",
    "score": 8,
    "total": 10,
    "created_at": "2023-06-15T14:30:00Z"
  }
]
```

#### POST /api/study_activities
- **Purpose**: Launch a study activity
- **Backend Responsibility**:
  - Create a new study session
  - Return launch information
- **Frontend Responsibility**:
  - Send group and activity selections
  - Open activity in new tab or redirect

**Request Format**:
```json
{
  "activity_id": 1,
  "group_id": 2
}
```

**Response Format**:
```json
{
  "session_id": 123,
  "activity_id": 1,
  "activity_name": "Flashcards",
  "activity_url": "/study/flashcards",
  "group_id": 2,
  "group_name": "Basic Phrases"
}
```

### 3. Words APIs

#### GET /api/words
- **Purpose**: List vocabulary words with pagination
- **Backend Responsibility**:
  - Return paginated list of words
  - Support ordering and filtering
- **Frontend Responsibility**:
  - Display words in a table
  - Handle pagination UI
  - Allow navigation to word details

**Query Parameters**:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 100)

**Response Format**:
```json
[
  {
    "id": 1,
    "japanese": "こんにちは",
    "romaji": "konnichiwa",
    "english": "hello",
    "correct_count": 5,
    "wrong_count": 1
  }
]
```

#### GET /api/words/:id
- **Purpose**: Get detailed information for a specific word
- **Backend Responsibility**:
  - Return word details including study stats
  - Include associated groups
- **Frontend Responsibility**:
  - Display word details
  - Show study statistics
  - List associated groups

**Response Format**:
```json
{
  "id": 1,
  "japanese": "こんにちは",
  "romaji": "konnichiwa",
  "english": "hello",
  "correct_count": 5,
  "wrong_count": 1,
  "groups": [
    {
      "id": 1,
      "name": "Basic Greetings"
    }
  ]
}
```

#### POST /api/words
- **Purpose**: Create a new vocabulary word
- **Backend Responsibility**:
  - Validate and store the new word
  - Associate with groups if specified
- **Frontend Responsibility**:
  - Provide form for word creation
  - Allow group associations
  - Handle validation errors

**Request Format**:
```json
{
  "japanese": "おはよう",
  "romaji": "ohayou",
  "english": "good morning",
  "group_ids": [1, 2]
}
```

**Response Format**:
```json
{
  "id": 125,
  "japanese": "おはよう",
  "romaji": "ohayou",
  "english": "good morning",
  "correct_count": 0,
  "wrong_count": 0
}
```

### 4. Groups APIs

#### GET /api/groups
- **Purpose**: List all word groups
- **Backend Responsibility**:
  - Return all groups with word counts
- **Frontend Responsibility**:
  - Display groups in a list or table
  - Allow navigation to group details

**Response Format**:
```json
[
  {
    "id": 1,
    "name": "Basic Greetings",
    "word_count": 10
  }
]
```

#### GET /api/groups/:id
- **Purpose**: Get details for a specific group
- **Backend Responsibility**:
  - Return group details and statistics
- **Frontend Responsibility**:
  - Display group information
  - Show group statistics

**Response Format**:
```json
{
  "id": 1,
  "name": "Basic Greetings",
  "word_count": 10,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

#### GET /api/groups/:id/words
- **Purpose**: Get words for a specific group
- **Backend Responsibility**:
  - Return paginated words in the group
- **Frontend Responsibility**:
  - Display words in a table
  - Handle pagination

**Query Parameters**:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 100)

**Response Format**:
```json
[
  {
    "id": 1,
    "japanese": "こんにちは",
    "romaji": "konnichiwa",
    "english": "hello",
    "correct_count": 5,
    "wrong_count": 1
  }
]
```

#### GET /api/groups/:id/study_sessions
- **Purpose**: Get study sessions for a specific group
- **Backend Responsibility**:
  - Return sessions for the group
- **Frontend Responsibility**:
  - Display session history
  - Allow navigation to session details

**Query Parameters**:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)

**Response Format**:
```json
[
  {
    "id": 1,
    "group_id": 1,
    "group_name": "Basic Phrases",
    "activity_id": 1,
    "activity_name": "Flashcards",
    "score": 8,
    "total": 10,
    "created_at": "2023-06-15T14:30:00Z"
  }
]
```

#### POST /api/groups
- **Purpose**: Create a new word group
- **Backend Responsibility**:
  - Validate and store the new group
  - Associate with words if specified
- **Frontend Responsibility**:
  - Provide form for group creation
  - Allow word associations
  - Handle validation errors

**Request Format**:
```json
{
  "name": "JLPT N5 Verbs",
  "word_ids": [1, 2, 3]
}
```

**Response Format**:
```json
{
  "id": 6,
  "name": "JLPT N5 Verbs",
  "word_count": 3
}
```

### 5. Study Sessions APIs

#### GET /api/study_sessions
- **Purpose**: List all study sessions
- **Backend Responsibility**:
  - Return paginated list of sessions
  - Include group and activity information
- **Frontend Responsibility**:
  - Display sessions in a table
  - Handle pagination
  - Allow navigation to session details

**Query Parameters**:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)

**Response Format**:
```json
[
  {
    "id": 1,
    "group_id": 1,
    "group_name": "Basic Phrases",
    "activity_id": 1,
    "activity_name": "Flashcards",
    "score": 8,
    "total": 10,
    "created_at": "2023-06-15T14:30:00Z"
  }
]
```

#### GET /api/study_sessions/:id
- **Purpose**: Get details for a specific study session
- **Backend Responsibility**:
  - Return session details
  - Include group and activity information
- **Frontend Responsibility**:
  - Display session details
  - Show score and statistics

**Response Format**:
```json
{
  "id": 1,
  "group_id": 1,
  "group_name": "Basic Phrases",
  "activity_id": 1,
  "activity_name": "Flashcards",
  "score": 8,
  "total": 10,
  "created_at": "2023-06-15T14:30:00Z"
}
```

#### GET /api/study_sessions/:id/words
- **Purpose**: Get words reviewed in a specific session
- **Backend Responsibility**:
  - Return words with review results
- **Frontend Responsibility**:
  - Display reviewed words
  - Show correct/incorrect status

**Response Format**:
```json
[
  {
    "id": 1,
    "word_id": 1,
    "japanese": "こんにちは",
    "romaji": "konnichiwa",
    "english": "hello",
    "correct": true,
    "created_at": "2023-06-15T14:30:00Z"
  }
]
```

#### POST /api/study/sessions
- **Purpose**: Create a new study session
- **Backend Responsibility**:
  - Create and store the session
  - Return session details
- **Frontend Responsibility**:
  - Send session data when completed
  - Display confirmation

**Request Format**:
```json
{
  "group_id": 1,
  "score": 8,
  "total": 10
}
```

**Response Format**:
```json
{
  "id": 124,
  "group_id": 1,
  "score": 8,
  "total": 10,
  "created_at": "2023-06-16T10:30:00Z"
}
```

### 6. Study Activity Tracking APIs

#### POST /api/study/word-stats
- **Purpose**: Update statistics for a word
- **Backend Responsibility**:
  - Update correct/wrong counts
- **Frontend Responsibility**:
  - Send update after each word review
  - Handle success/failure responses

**Request Format**:
```json
{
  "word_id": 1,
  "correct": true
}
```

**Response Format**:
```json
{
  "success": true
}
```

#### POST /api/study/activities
- **Purpose**: Record a study activity for a word
- **Backend Responsibility**:
  - Store the activity record
- **Frontend Responsibility**:
  - Send record for each reviewed word
  - Handle success/failure responses

**Request Format**:
```json
{
  "word_id": 1,
  "session_id": 124,
  "correct": true
}
```

**Response Format**:
```json
{
  "success": true
}
```

### 7. Settings APIs

#### POST /api/reset_history
- **Purpose**: Reset all study history
- **Backend Responsibility**:
  - Delete all study sessions and activities
  - Reset word statistics
- **Frontend Responsibility**:
  - Provide confirmation dialog
  - Handle success/failure responses
  - Update UI after reset

**Response Format**:
```json
{
  "success": true,
  "message": "Study history has been reset"
}
```

#### POST /api/full_reset
- **Purpose**: Perform a full database reset
- **Backend Responsibility**:
  - Reset all data to initial state
  - Reseed with default data
- **Frontend Responsibility**:
  - Provide confirmation dialog
  - Handle success/failure responses
  - Redirect to dashboard after reset

**Response Format**:
```json
{
  "success": true,
  "message": "System has been fully reset"
}
```

## Error Handling

All API endpoints follow a consistent error response format:

```json
{
  "error": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- `200 OK`: Successful GET, PUT, or DELETE request
- `201 Created`: Successful POST request that created a new resource
- `400 Bad Request`: Invalid request parameters or body
- `404 Not Found`: Requested resource does not exist
- `500 Internal Server Error`: Server-side error

## API Implementation Considerations

### Backend Implementation

1. **Use Repository Pattern**:
   - Separate database access from business logic
   - Create repositories for each entity (words, groups, sessions)

2. **Service Layer**:
   - Implement business logic in service objects
   - Handle validation and error checking

3. **Controllers/Handlers**:
   - Keep handlers thin, delegating to services
   - Handle request parsing and response formatting

### Frontend Implementation

1. **Service Objects**:
   - Create service objects for API interactions
   - Handle error responses and retries

2. **State Management**:
   - Cache responses when appropriate
   - Update local state after mutations

3. **Error Handling**:
   - Display user-friendly error messages
   - Provide retry options for failed requests 