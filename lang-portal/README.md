# Language Learning Portal Backend

This is a Go-based backend server for a language learning portal. The portal serves three main purposes:
- Managing vocabulary inventory
- Recording study results (Learning Record Store)
- Acting as a unified launchpad for various learning applications

## Technical Stack

- **Language**: Go
- **Database**: SQLite3
- **API Framework**: Gin
- **Task Runner**: Mage

## Project Structure

```
lang-portal/
├── cmd/
│   └── server/                # Contains the main entry point for launching the server.
├── internal/
│   ├── models/                # Data structures and database operations.
│   ├── handlers/              # HTTP handlers, organized by feature.
│   └── service/               # Business logic and application services.
├── db/
│   ├── migrations/            # SQL migration files to create or update database schema.
│   └── seeds/                 # JSON seed files for initial data population.
├── magefile.go                # Mage task definitions.
├── setup_db.go                # Simple database setup script.
├── go.mod                     # Go module file.
└── words.db                   # SQLite3 database file (located at the project root).
```

## Setup and Installation

### Prerequisites

- Go 1.18 or higher
- SQLite development libraries

### Installation on Ubuntu/WSL

1. Install Go and SQLite dependencies:
   ```bash
   sudo apt update
   sudo apt install golang-go gcc pkg-config libsqlite3-dev
   ```

2. Clone the repository and navigate to the project directory:
   ```bash
   cd /path/to/lang-portal
   ```

3. Download Go dependencies:
   ```bash
   go mod download
   ```

4. Set up the database:
   ```bash
   go run setup_db.go
   ```

5. Run the server:
   ```bash
   go run cmd/server/main.go
   ```

The server will be available at http://localhost:8080

## API Endpoints and Examples

### Dashboard Endpoints

- **GET /api/dashboard/last_study_session**: Get the most recent study session
  ```bash
  curl http://localhost:8080/api/dashboard/last_study_session
  ```
  Example response:
  ```json
  {"id":1,"group_id":1,"created_at":"2025-03-04T23:18:57.162180031-06:00","study_activity_id":1,"group_name":"Basic Greetings"}
  ```

- **GET /api/dashboard/study_progress**: Get study progress statistics
  ```bash
  curl http://localhost:8080/api/dashboard/study_progress
  ```
  Example response:
  ```json
  {"total_available_words":10,"total_words_studied":0}
  ```

### Word Endpoints

- **GET /api/words**: Get all vocabulary words
  ```bash
  curl http://localhost:8080/api/words
  ```
  
- **GET /api/words/:id**: Get a specific word by ID
  ```bash
  curl http://localhost:8080/api/words/1
  ```

### Group Endpoints

- **GET /api/groups**: Get all word groups
  ```bash
  curl http://localhost:8080/api/groups
  ```
  Example response:
  ```json
  [{"id":1,"name":"Basic Greetings"},{"id":2,"name":"Common Phrases"},{"id":3,"name":"Daily Conversations"}]
  ```
  
- **GET /api/groups/:id**: Get a specific group by ID
  ```bash
  curl http://localhost:8080/api/groups/1
  ```
  
- **GET /api/groups/:id/words**: Get all words in a specific group
  ```bash
  curl http://localhost:8080/api/groups/1/words
  ```

### Study Activity Endpoints

- **GET /api/activities**: Get all study activities
  ```bash
  curl http://localhost:8080/api/activities
  ```
  
- **GET /api/activities/:id**: Get a specific study activity by ID
  ```bash
  curl http://localhost:8080/api/activities/1
  ```
  
- **POST /api/study_activities**: Create a new study session
  ```bash
  curl -X POST -H "Content-Type: application/json" -d '{"group_id": 1, "study_activity_id": 1}' http://localhost:8080/api/study_activities
  ```
  Example response:
  ```json
  {"id":1,"group_id":1}
  ```

### System Endpoints

- **POST /api/reset_history**: Reset study history
  ```bash
  curl -X POST http://localhost:8080/api/reset_history
  ```
  
- **POST /api/full_reset**: Perform a complete system reset
  ```bash
  curl -X POST http://localhost:8080/api/full_reset
  ```

## Database Schema

The database includes the following tables:

- **words**: Stores vocabulary words
- **groups**: Thematic groups of words
- **words_groups**: Join table linking words to groups
- **study_activities**: Available learning activities
- **study_sessions**: Records of study sessions
- **words_studied**: Records of word practice results

## Troubleshooting

If you encounter any issues:

1. **Database Access Errors**: Make sure SQLite development libraries are installed
   ```bash
   sudo apt install libsqlite3-dev
   ```

2. **Missing Go Dependencies**: Ensure all dependencies are downloaded
   ```bash
   go mod download
   ```

3. **Server Already Running**: Check if port 8080 is already in use
   ```bash
   sudo lsof -i :8080
   ```

4. **Permission Issues**: Ensure you have write permissions in the project directory for database creation