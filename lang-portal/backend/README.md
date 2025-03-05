# Language Learning Portal Backend

A robust Go API that powers the Language Learning Portal application.

## Overview

The backend of the Language Learning Portal is a Go application that provides a RESTful API for managing vocabulary words, word groups, study activities, and study sessions. It handles data persistence, business logic, and serves the frontend application.

## Technology Stack

- **Language**: Go (Golang)
- **Web Framework**: Gin
- **Database**: SQLite (development), PostgreSQL (production)
- **ORM**: Custom data access layer
- **Testing**: Go's standard testing package, Testify
- **Documentation**: Swagger via go-swagger
- **Build Tool**: Go modules

## Project Structure

```
backend/
├── cmd/
│   └── server/              # Application entry points
│       └── main.go          # Main server executable
├── internal/
│   ├── handlers/            # HTTP request handlers
│   ├── models/              # Data models and database access
│   ├── service/             # Business logic services
│   └── middleware/          # HTTP middleware components
├── db/
│   └── migrations/          # Database migration files
├── test/                    # Integration and E2E tests
│   ├── api_test.go          # API tests
│   └── e2e_test.go          # End-to-end tests
├── go.mod                   # Go module definition
├── go.sum                   # Go module checksums
└── README.md                # This file
```

## Key Features

- **Vocabulary Management**: CRUD operations for Japanese vocabulary words
- **Group Organization**: CRUD operations for word groups and word-group associations
- **Study Activities**: Pre-defined study methods with configurable settings
- **Study Sessions**: Record and retrieve study session history and results
- **Authentication**: User authentication and authorization
- **Data Validation**: Robust input validation and error handling
- **Swagger Documentation**: Interactive API documentation

## API Endpoints

The API follows RESTful conventions and is organized by resource:

### Words API

- `GET /api/words` - Get all words
- `GET /api/words/{id}` - Get word by ID
- `POST /api/words` - Create a new word
- `PUT /api/words/{id}` - Update a word
- `DELETE /api/words/{id}` - Delete a word
- `GET /api/words/{id}/groups` - Get groups containing a word

### Groups API

- `GET /api/groups` - Get all groups
- `GET /api/groups/{id}` - Get group by ID
- `POST /api/groups` - Create a new group
- `PUT /api/groups/{id}` - Update a group
- `DELETE /api/groups/{id}` - Delete a group
- `GET /api/groups/{id}/words` - Get words in a group
- `POST /api/groups/{id}/words/{wordId}` - Add word to group
- `DELETE /api/groups/{id}/words/{wordId}` - Remove word from group

### Study Activities API

- `GET /api/study-activities` - Get all study activities
- `GET /api/study-activities/{id}` - Get study activity by ID
- `POST /api/study-activities/{id}/launch` - Launch a study session
- `GET /api/study-activities/{id}/sessions` - Get sessions for an activity

### Study Sessions API

- `GET /api/study-sessions` - Get all study sessions
- `GET /api/study-sessions/{id}` - Get session by ID
- `PUT /api/study-sessions/{id}/complete` - Complete a study session
- `GET /api/groups/{id}/study-sessions` - Get sessions for a group

### Dashboard API

- `GET /api/dashboard/stats` - Get user dashboard statistics
- `GET /api/dashboard/recent-activity` - Get recent study activity

## Database Schema

The application uses the following core entities:

### Words

Store vocabulary words with Japanese, romaji, and English translations.

```sql
CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    japanese TEXT NOT NULL,
    romaji TEXT NOT NULL,
    english TEXT NOT NULL,
    notes TEXT,
    difficulty INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Groups

Organize words into thematic collections.

```sql
CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Words-Groups Association

Many-to-many relationship between words and groups.

```sql
CREATE TABLE word_group (
    word_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    PRIMARY KEY (word_id, group_id),
    FOREIGN KEY (word_id) REFERENCES words(id),
    FOREIGN KEY (group_id) REFERENCES groups(id)
);
```

### Study Activities

Define different study methods and their configurations.

```sql
CREATE TABLE study_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    type TEXT NOT NULL,
    settings TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Study Sessions

Record study sessions and their results.

```sql
CREATE TABLE study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    score REAL,
    total_words INTEGER NOT NULL,
    correct_answers INTEGER,
    incorrect_answers INTEGER,
    status TEXT NOT NULL,
    results TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (activity_id) REFERENCES study_activities(id),
    FOREIGN KEY (group_id) REFERENCES groups(id)
);
```

## Getting Started

### Prerequisites

- Go 1.16 or higher
- SQLite (included in Go standard library)
- PostgreSQL 14 or higher (optional)

### Development Setup

1. Clone the repository and navigate to the backend directory:
   ```bash
   git clone https://github.com/your-organization/lang-portal.git
   cd lang-portal/backend
   ```

2. Install dependencies:
   ```bash
   go mod download
   ```

3. Run the application:
   ```bash
   go run cmd/server/main.go
   ```

4. Access the API at http://localhost:8080/api

5. Access Swagger documentation at http://localhost:8080/swagger/index.html

### Running Tests

```bash
go test ./... -v
```

### Building for Production

```bash
go build -o langportal ./cmd/server
```

This creates an executable in the current directory.

## API Documentation

The API documentation is automatically generated using Swagger and can be accessed at:

```
http://localhost:8080/swagger/index.html
```

This provides an interactive interface to explore all API endpoints, their parameters, request bodies, and responses.

## Error Handling

The API uses consistent error handling with appropriate HTTP status codes:

- `400 Bad Request` - Invalid input data
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., duplicate entry)
- `500 Internal Server Error` - Unexpected server error

Error responses follow this format:

```json
{
  "error": "Not Found",
  "message": "Word with ID 999 not found",
  "status": 404,
  "timestamp": "2025-03-10T15:40:03Z"
}
```

## Security

The application implements security best practices:

- JWT-based authentication
- Role-based access control
- Password hashing
- Input validation and sanitization
- Rate limiting

## Configuration

The application uses environment variables and configuration files for environment-specific settings:

- **Development**: Uses SQLite by default
- **Production**: Can be configured to use PostgreSQL

Key configuration parameters:

```
# Database Configuration
DB_TYPE=sqlite
DB_PATH=./words.db
# Or for PostgreSQL
# DB_TYPE=postgres
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=langportal
# DB_USER=postgres
# DB_PASSWORD=yourpassword

# Server Configuration
PORT=8080
```

## Logging

The application uses Go's standard logging package with configurable log levels:

- Debug: Detailed information for debugging
- Info: General operational information
- Warning: Potential issues that don't affect normal operation
- Error: Errors that affect specific operations but not the entire application
- Fatal: Critical errors that require application shutdown

## Performance Optimizations

- Database connection pooling
- Query optimization with indexes
- Response caching for frequently accessed data
- Pagination for large result sets

## Contributing

Please read the [Contributing Guide](../CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Troubleshooting

### Common Issues

1. **Database Connection Problems**:
   - For SQLite: Check file permissions on the database file
   - For PostgreSQL: Verify PostgreSQL is running with `pg_isready`
   - Check connection parameters in configuration

2. **Application Won't Start**:
   - Check port availability: `netstat -tuln | grep 8080`
   - Verify Go version: `go version`
   - Check logs for detailed errors

3. **Test Failures**:
   - Run with verbose output: `go test -v ./...`
   - Check for environment-specific issues
   - Ensure test database is properly initialized

### Support

For additional help, please open an issue on the GitHub repository or contact the development team. 