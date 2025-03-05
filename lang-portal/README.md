# Language Learning Portal

A comprehensive web application for language learning, featuring vocabulary management, study activities, progress tracking, and personalized learning experiences.

## Project Overview

The Language Learning Portal is a full-stack application designed to help users learn new languages through various interactive activities. The application consists of a React frontend with TypeScript and a Go backend with SQLite database, providing a complete solution for vocabulary management and study tracking.

![Project Architecture](docs/architecture-diagram.png)

## Directory Structure

```
language-learning-portal/
├── frontend/             # React frontend application
│   ├── src/              # Frontend source code
│   ├── public/           # Static assets
│   ├── README.md         # Frontend-specific documentation
│   └── ...               # Other frontend files
├── backend/              # Go backend application
│   ├── cmd/              # Application entry points
│   ├── internal/         # Private application code
│   ├── db/               # Database scripts and migrations
│   ├── README.md         # Backend-specific documentation
│   └── ...               # Other backend files
├── docs/                 # Project documentation
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## Tech Stack

### Frontend
- **React 18** - UI library for building component-based interfaces
- **TypeScript** - Static typing for enhanced development experience
- **styled-components** - CSS-in-JS library for component styling
- **React Router v6** - Declarative routing
- **Vite** - Fast build tool with HMR
- **Context API** - State management
- **Material UI Icons** - Icon library
- **date-fns** - Date utility library

### Backend
- **Go** - Primary programming language
- **SQLite** - Embedded database
- **Chi Router** - HTTP routing
- **Mage** - Build automation tool
- **Go Validator** - Request validation
- **CORS Middleware** - Cross-origin support

## Key Features

### 1. Interactive Dashboard
- Overview of learning progress
- Recent activity summary
- Quick stats and learning metrics
- Direct access to study features

### 2. Vocabulary Management
- Create, read, update, and delete vocabulary words
- Support for non-Latin scripts (e.g., Japanese with furigana)
- Notes, examples, and difficulty ratings
- Search and filter capabilities

### 3. Group Organization
- Organize words into thematic collections
- Study specific word groups
- Track progress by group
- Smart grouping suggestions

### 4. Study Activities
- **Flashcards**: Traditional flashcard study with spaced repetition
- **Multiple Choice**: Test comprehension with multiple choice questions
- **Typing Practice**: Improve recall by typing translations
- **Matching Game**: Pair words and translations in an interactive game

### 5. Progress Tracking
- Detailed session history
- Performance metrics and analytics
- Learning trends visualization
- Spaced repetition algorithm for optimal learning

### 6. Global Search
- Search across words, groups, and sessions
- Advanced filtering options
- Highlighted search results
- Quick access to content from anywhere in the app

### 7. Customization
- Personalized settings
- Theme selection (light/dark)
- Study mode preferences
- Learning path customization

## System Architecture

The application follows a client-server architecture:

1. **Frontend (Client)**
   - React-based Single Page Application
   - Component-based architecture organized by feature
   - Responsive design for all devices
   - Client-side routing

2. **Backend (Server)**
   - RESTful API built with Go
   - Clean architecture with separation of concerns
   - Data persistence with SQLite
   - Resource-based routing

3. **Data Flow**
   - Frontend makes API requests to backend
   - Backend processes requests and interacts with database
   - Backend returns structured JSON responses
   - Frontend renders UI based on response data

## Getting Started

### Prerequisites
- Node.js (v14+) for frontend development
- Go (v1.16+) for backend development
- npm or yarn package manager
- Git

### Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/farabi1038/free-genai-bootcamp-2025/tree/50bf88c76963081741fa297750f74c52bbd2752e/lang-portal
cd lang-portal
```

2. Set up the backend:
```bash
cd backend
go mod download
go run setup_db.go
```

3. Run the backend server:
```bash
# Using Mage
mage run

# Or directly with Go
go run cmd/server/main.go
```

4. Set up the frontend:
```bash
cd ../frontend
npm install  # or yarn install
```

5. Run the frontend development server:
```bash
npm run dev  # or yarn dev
```

6. Open your browser and visit:
   - Frontend: http://localhost:5173 #check beforehand
   - Backend API: http://localhost:8080/api #check beforehand

## Development Workflow

### Running Both Services

For local development, you'll need to run both the frontend and backend services:

1. Terminal 1 (Backend):
```bash
cd backend
mage run
```

2. Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

### API Integration

The frontend communicates with the backend through API services defined in `frontend/src/api/`. These services handle:

- Authentication and authorization
- Data fetching and persistence
- Error handling and retries
- Request/response transformation

Example API usage:
```typescript
// In a React component
import { wordService } from '../api/wordService';

// Fetch words
const words = await wordService.getAllWords();

// Add a new word
const newWord = await wordService.createWord({
  japanese: '猫',
  romaji: 'neko',
  english: 'cat'
});
```

## Frontend Architecture

The frontend follows a component-based architecture organized by feature. See [frontend/README.md](frontend/README.md) for detailed component documentation.

### Key Components

- **Dashboard Components**: Overview of learning progress
- **Word Components**: Vocabulary management
- **Group Components**: Collection management
- **Study Components**: Learning activities
- **UI Components**: Reusable design system

### State Management

- **Context API** for application-wide state
- **Component-local state** for component-specific concerns
- **URL parameters** for navigation state

## Backend Architecture

The backend follows a clean architecture pattern with clear separation of concerns. See [backend/README.md](backend/README.md) for detailed API documentation.

### Key API Endpoints

- **Words API**: Vocabulary management
- **Groups API**: Collection management
- **Activities API**: Study method definitions
- **Sessions API**: Learning history
- **Dashboard API**: Statistics and metrics

### Database Schema

The application uses SQLite with tables for words, groups, activities, sessions, and relationships between them.

## Deployment

### Frontend Deployment

Build the frontend for production:
```bash
cd frontend
npm run build
```

The output will be in the `dist` directory, which can be served by any static file server.

### Backend Deployment

Build the backend for production:
```bash
cd backend
mage build
```

This creates an executable that can be deployed to any server supporting Go applications.

## Contributing

We welcome contributions to the Language Learning Portal! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The Nord color palette for UI design
- Open source libraries and tools that made this project possible
- Language learning research that informed our study methods