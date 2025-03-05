# Language Learning Portal Test Plan

This document outlines the comprehensive testing strategy for ensuring the Language Learning Portal's frontend and backend work smoothly together.

## Test Categories

The test suite is organized into four main categories:

1. **Frontend Unit Tests**
   - Test individual React components in isolation
   - Verify UI behavior and state management
   - Mock API calls to focus on component logic

2. **Backend Unit Tests**
   - Test individual API endpoints and services
   - Verify data processing and business logic
   - Use in-memory database for fast execution

3. **Backend End-to-End Tests**
   - Test the full API flow from endpoints to database
   - Verify integration between controllers, services, and repositories
   - Test error handling and edge cases

4. **Frontend-Backend Integration Tests**
   - Test the communication between frontend and backend
   - Verify data format consistency
   - Ensure error handling works across the stack

## Test Implementations

### Frontend Tests

The frontend tests are implemented using:
- **Vitest**: A fast test runner compatible with Vite
- **React Testing Library**: For testing React components
- **MSW (Mock Service Worker)**: For mocking API responses in component tests

Key test files:
- `frontend/src/test/api/groupService.test.ts`: Tests the GroupService API client
- `frontend/src/test/components/GroupList.test.tsx`: Tests the GroupList component
- `frontend/src/test/integration/api-integration.test.ts`: Tests frontend-backend communication

### Backend Tests

The backend tests are implemented using:
- **Go Testing Package**: The standard Go testing framework
- **Testify**: Assertions and test utilities
- **SQLite in-memory DB**: For fast test execution without persistence

Key test files:
- `backend/test/api_test.go`: Tests individual API endpoints
- `backend/test/e2e_test.go`: Tests complete user workflows

## Running Tests

A comprehensive test script (`test-integration.sh`) has been created to:

1. Verify the backend is running (starts it if needed)
2. Verify the frontend dev server is running (starts it if needed)
3. Run backend unit tests
4. Run backend end-to-end tests
5. Run frontend unit tests
6. Run integration tests
7. Provide a comprehensive test report

To run all tests:

```bash
./test-integration.sh
```

## Test Coverage

The test suite aims to cover:

- **API Contract**: Ensure frontend and backend agree on data formats
- **Error Handling**: Verify errors are properly handled on both sides
- **User Workflows**: Test complete user journeys from UI to database and back
- **Edge Cases**: Test boundary conditions and invalid inputs

## Continuous Integration

For CI/CD pipelines, the tests can be run with:

```bash
# Backend tests
cd backend && go test ./... -v

# Frontend tests
cd frontend && npm test

# Integration tests
cd frontend && npm test -- "integration"
```

## Adding New Tests

### Frontend

To add new frontend tests:

1. For components, create files named `ComponentName.test.tsx` in the same directory as the component
2. For services, create files named `serviceName.test.ts` in the `test/api` directory
3. For integration, add test cases to the existing integration test files

### Backend

To add new backend tests:

1. For API endpoints, add test cases to `api_test.go`
2. For end-to-end workflows, add test cases to `e2e_test.go`
3. For new controllers/services, create dedicated test files in the appropriate packages

## Test Data

The test suite uses a combination of:

- **Mock data**: For isolated component tests
- **In-memory test database**: For backend unit tests
- **Actual running servers**: For integration tests

## Troubleshooting

If tests are failing, check:

1. **Backend server**: Ensure it's running on port 8080
2. **Frontend dev server**: Ensure it's running on port 3000
3. **Database**: Ensure the test database is properly initialized
4. **API changes**: If the API contract changed, update the tests to match

## Future Improvements

Planned enhancements to the test suite:

1. Add visual regression testing for UI components
2. Implement performance tests to measure API response times
3. Add accessibility testing to ensure the app is usable by everyone
4. Implement cross-browser testing using Selenium or Cypress 