# Language Learning Portal - Setup Guide

This document provides comprehensive instructions for setting up, running, and testing the Language Learning Portal application.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Go** (v1.16 or later)
  - [Download Go](https://golang.org/dl/)
  - Verify with: `go version`

- **Node.js** (v16 or later) and npm
  - [Download Node.js](https://nodejs.org/)
  - Verify with: `node -v` and `npm -v`

- **PostgreSQL** (v14 or later)
  - [Download PostgreSQL](https://www.postgresql.org/download/)
  - Verify with: `psql --version`

- **Git**
  - [Download Git](https://git-scm.com/downloads)
  - Verify with: `git --version`

## Quick Start

For those who want to get started quickly:

```bash
# Clone the repository (if you haven't already)
git clone https://github.com/your-organization/lang-portal.git
cd lang-portal

# Start both frontend and backend with the convenience script
./test-integration.sh
```

This script will:
1. Check if the backend is running (starts it if not)
2. Check if the frontend is running (starts it if not)
3. Run tests to verify everything is working

Access the application at http://localhost:3000

## Detailed Setup

### Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Install Go dependencies**:
   ```bash
   go mod download
   ```

3. **Set up the database**:
   ```bash
   # Create PostgreSQL database
   createdb langportal

   # Run database migrations
   go run magefile.go migrate
   ```

4. **Configure the backend**:
   - Review `application.properties` file
   - For development, you can use the default settings

5. **Start the backend server**:
   ```bash
   go run cmd/server/main.go
   ```

The backend server will start on http://localhost:8080

### Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install npm dependencies**:
   ```bash
   npm install
   ```

3. **Configure the frontend**:
   - The frontend is preconfigured to connect to the backend at http://localhost:8080/api
   - This is set up in the Vite configuration file (`vite.config.ts`)

4. **Start the frontend development server**:
   ```bash
   npm run dev
   ```

The frontend development server will start on http://localhost:3000

## Running the Application

### Development Mode

1. **Start the backend** (in one terminal):
   ```bash
   cd backend
   go run cmd/server/main.go
   ```

2. **Start the frontend** (in another terminal):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application** at http://localhost:3000

### Production Build

1. **Build the frontend**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Build the backend**:
   ```bash
   cd backend
   go build -o langportal ./cmd/server
   ```

3. **Run the production server**:
   ```bash
   cd backend
   ./langportal
   ```

## Testing

We have a comprehensive test suite to ensure the application works correctly:

```bash
# Run all tests (frontend, backend, and integration)
./test-integration.sh

# Run only backend tests
cd backend
go test ./... -v

# Run only frontend tests
cd frontend
npm test

# Run with watch mode (frontend)
cd frontend
npm run test:watch

# Run with coverage report
cd frontend
npm run test:coverage
```

See the [TEST-PLAN.md](TEST-PLAN.md) document for more details on our testing strategy.

## Documentation

The project includes detailed documentation in various files:

- **[README.md](README.md)**: General project overview and introduction
- **[frontend/README.md](frontend/README.md)**: Frontend-specific documentation
- **[backend/README.md](backend/README.md)**: Backend-specific documentation
- **[TEST-PLAN.md](TEST-PLAN.md)**: Comprehensive testing strategy
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Guidelines for contributing to the project
- **[frontend/docs/API-INTEGRATION.md](frontend/docs/API-INTEGRATION.md)**: Details on frontend-backend integration

## Troubleshooting

### Common Issues

1. **Backend fails to start**
   - Check PostgreSQL is running: `pg_isready`
   - Verify database connection settings in `application.properties`
   - Check logs for specific errors: `cat backend.log`

2. **Frontend fails to start**
   - Verify Node.js version: `node -v`
   - Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
   - Check for port conflicts: `netstat -tuln | grep 3000`

3. **Frontend can't connect to backend**
   - Ensure backend is running on port 8080
   - Check the proxy settings in `vite.config.ts`
   - Look for CORS errors in the browser developer console

4. **Tests are failing**
   - Make sure both frontend and backend are running
   - Check for API changes that might affect test expectations
   - Review the specific test failures in the logs

### Getting Help

If you encounter issues not covered here:

1. Check the GitHub issues for similar problems
2. Join our developer Discord channel
3. Reach out to the maintainers listed in CONTRIBUTING.md 