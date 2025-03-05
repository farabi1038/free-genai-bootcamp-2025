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

## Testing

The application includes a comprehensive test suite that verifies all API endpoints. The tests use an in-memory SQLite database to ensure they're fast and don't interfere with your development database.

### Running Tests

To run the tests:

```bash
# Run from the project root
./test/run_tests.sh
```

This will:
1. Execute all tests in the test package
2. Generate a coverage report
3. Display the coverage statistics

### Test Results

When running the tests, you should see output similar to the following:

```
=== RUN   TestGetAllWords
[GIN] 2025/03/04 - 23:33:58 | 200 | 788.874µs | | GET "/api/words"
--- PASS: TestGetAllWords (0.00s)
=== RUN   TestGetWordByID
[GIN] 2025/03/04 - 23:33:58 | 200 | 85.879µs | | GET "/api/words/1"
--- PASS: TestGetWordByID (0.00s)
=== RUN   TestGetAllGroups
[GIN] 2025/03/04 - 23:33:58 | 200 | 71.387µs | | GET "/api/groups"
--- PASS: TestGetAllGroups (0.00s)
...
PASS
ok      github.com/free-genai-bootcamp-2025/lang-portal/test    0.018s
```

All tests should pass, confirming that your API endpoints are working correctly.

### Test Structure

The tests are organized as follows:

- `test/api_test.go`: Contains all API endpoint tests
- `internal/models/test_helpers.go`: Contains helper functions for setting up test data

The test suite:
1. Creates an in-memory SQLite database
2. Applies the application schema
3. Seeds test data
4. Sets up a test Gin router
5. Runs all endpoint tests against this router

### Test Coverage

The test suite covers all major API endpoints:
- `/api/words` endpoints
- `/api/groups` endpoints
- `/api/study_activities` endpoints
- `/api/dashboard` endpoints
- `/api/reset_history` and `/api/full_reset` endpoints

### Writing New Tests

If you add new functionality, follow these steps to create tests:

1. Add a new test function in `test/api_test.go`
2. Use the `performRequest` helper function to simulate HTTP requests
3. Verify the response status code and body content
4. Run the tests to ensure they pass

### Example Test

```go
func TestExampleEndpoint(t *testing.T) {
    // Set up any required data
    requestBody := map[string]string{
        "key": "value",
    }
    
    // Perform the request
    resp := performRequest("POST", "/api/your_endpoint", requestBody)
    
    // Check the status code
    if resp.Code != http.StatusOK {
        t.Errorf("Expected status code %d, got %d", http.StatusOK, resp.Code)
    }
    
    // Parse and check the response
    var response map[string]interface{}
    json.Unmarshal(resp.Body.Bytes(), &response)
    
    // Assert on expected values
    if response["result"] != "expected" {
        t.Errorf("Expected result 'expected', got %v", response["result"])
    }
}
```

### Integration with Development Workflow

Running tests should be part of your regular development workflow:

1. **Before making changes**: Run tests to ensure everything works correctly
2. **After making changes**: Run tests again to verify your changes didn't break existing functionality
3. **When adding new features**: Add tests for the new functionality

### Common Test Issues

- **Table not found errors**: Check that the table names in your tests match the ones in your schema
- **Failed assertions**: Verify that your API returns the expected data format
- **Missing dependencies**: Ensure all required packages are imported in your tests

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