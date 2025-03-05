# Language Learning Portal - Frontend

This is the frontend for the Language Learning Portal, a modern React application built with TypeScript, styled-components, and Vite. This application provides an interactive platform for language learning with various study activities and vocabulary management features.

## Tech Stack

- **React 18** - UI library for building component-based interfaces
- **TypeScript** - Adds static typing to enhance development experience and code quality
- **styled-components** - CSS-in-JS library for component-level styling with theme support
- **React Router v6** - Declarative routing for React applications
- **Vite** - Fast build tool with HMR (Hot Module Replacement)
- **Context API** - For state management and data sharing between components
- **Material UI Icons** - Icon library for visual elements
- **date-fns** - Modern JavaScript date utility library

## Architecture

The frontend follows a component-based architecture organized by feature:

```
src/
├── api/                # API service layer for data fetching
│   ├── dashboardService.ts  # Dashboard data fetching and metrics
│   ├── groupService.ts      # Group management operations
│   ├── mockService.ts       # Mock data generation for development
│   ├── searchService.ts     # Global search functionality 
│   ├── sessionService.ts    # Study session tracking and results
│   ├── types.ts             # Type definitions for API data
│   └── wordService.ts       # Word management operations
├── components/         # React components organized by feature
│   ├── dashboard/      # Dashboard and statistics components
│   │   ├── DashboardPage.tsx          # Main dashboard view
│   │   ├── LastStudySessionCard.tsx   # Shows last study session
│   │   ├── StudyProgressCard.tsx      # Displays overall progress
│   │   ├── QuickStatsCard.tsx         # Shows key metrics
│   │   └── StartStudyingCard.tsx      # Quick-start component
│   ├── groups/         # Group management components
│   │   ├── GroupsPage.tsx             # Groups listing page
│   │   ├── GroupDetails.tsx           # Detailed view of a group
│   │   ├── GroupCard.tsx              # Card for group listings
│   │   ├── AddGroupModal.tsx          # Modal for creating groups
│   │   └── EditGroupModal.tsx         # Modal for editing groups
│   ├── layout/         # Layout components
│   │   ├── Navbar.tsx                 # Top navigation bar
│   │   ├── Sidebar.tsx                # Side navigation menu
│   │   ├── MainLayout.tsx             # Layout wrapper
│   │   ├── ErrorBoundary.tsx          # Error handling component
│   │   └── LoadingSpinner.tsx         # Loading indicator
│   ├── search/         # Search components
│   │   ├── SearchBar.tsx              # Global search input
│   │   ├── SearchResults.tsx          # Search results display
│   │   ├── SearchResultItem.tsx       # Individual search result
│   │   └── SearchFilters.tsx          # Filtering options for search
│   ├── settings/       # User settings components
│   │   ├── SettingsPage.tsx           # Main settings page
│   │   ├── ThemeToggle.tsx            # Light/dark mode toggle
│   │   ├── LanguageSelector.tsx       # UI language selection
│   │   └── ResetButton.tsx            # Reset application state
│   ├── study/          # Study-related components
│   │   ├── ActivitySelector.tsx       # Study activity chooser
│   │   ├── SessionSummary.tsx         # Study session results
│   │   ├── StudyHeader.tsx            # Header for study sessions
│   │   ├── StudyControls.tsx          # Navigation controls for study
│   │   ├── Timer.tsx                  # Session timer component
│   │   ├── activities/                # Study activity components
│   │   │   ├── FlashcardActivity.tsx  # Flashcard study component
│   │   │   │   ├── Flashcard.tsx      # Individual flashcard
│   │   │   │   └── FlashcardControls.tsx # Flip/navigation controls
│   │   │   ├── MatchingActivity.tsx   # Word matching activity
│   │   │   │   ├── MatchingCard.tsx   # Card for matching game
│   │   │   │   └── MatchingBoard.tsx  # Game board for matching
│   │   │   ├── MultipleChoiceActivity.tsx # Quiz activity
│   │   │   │   ├── Question.tsx       # Quiz question component
│   │   │   │   └── AnswerOptions.tsx  # Answer selection component
│   │   │   └── TypingActivity.tsx     # Typing practice activity
│   │   │       ├── TypingPrompt.tsx   # Word to be typed
│   │   │       └── TypingInput.tsx    # Text input with validation
│   │   └── sessions/                  # Study session components
│   │       ├── SessionsPage.tsx       # Study history list
│   │       ├── SessionDetails.tsx     # Detailed session view
│   │       └── SessionCard.tsx        # Card for session listings
│   ├── ui/             # Reusable UI components
│   │   ├── Button.tsx                 # Custom button component
│   │   ├── Card.tsx                   # Card container
│   │   ├── Modal.tsx                  # Modal dialog
│   │   ├── TextField.tsx              # Text input
│   │   ├── Dropdown.tsx               # Dropdown selector
│   │   ├── ProgressBar.tsx            # Progress indicator
│   │   ├── Tag.tsx                    # Label/tag component
│   │   ├── Alert.tsx                  # Alert/notification component
│   │   ├── Tooltip.tsx                # Tooltip component
│   │   └── charts/                    # Chart components
│   │       ├── BarChart.tsx           # Bar chart visualization
│   │       ├── LineChart.tsx          # Line chart for trends
│   │       └── PieChart.tsx           # Pie chart for proportions
│   └── words/          # Word management components
│       ├── WordsPage.tsx              # Words listing page
│       ├── WordDetails.tsx            # Detailed word view
│       ├── WordCard.tsx               # Card for word listings
│       ├── AddWordModal.tsx           # Modal for creating words
│       ├── EditWordModal.tsx          # Modal for editing words
│       ├── WordForm.tsx               # Form for word data entry
│       └── JapaneseWordDisplay.tsx    # Japanese word with furigana
├── contexts/           # React contexts for state management
│   ├── SearchContext.tsx     # Global search state management
│   ├── SettingsContext.tsx   # User preferences and settings
│   ├── ThemeContext.tsx      # Theme (light/dark) management
│   └── AuthContext.tsx       # Authentication state (future use)
├── styles/             # Global styles and theme
│   ├── GlobalStyle.ts         # Global CSS styles
│   ├── theme.ts               # Theme configuration with Nord palette
│   ├── animations.ts          # Reusable animations
│   └── mediaQueries.ts        # Responsive breakpoints
├── hooks/              # Custom React hooks
│   ├── useLocalStorage.ts     # Hook for local storage management
│   ├── useDebounce.ts         # Hook for debouncing function calls
│   ├── useForm.ts             # Form state management hook
│   └── useApi.ts              # API request hook with loading states
├── utils/              # Utility functions
│   ├── formatters.ts          # Data formatting helpers
│   ├── validators.ts          # Input validation functions
│   └── localStorage.ts        # Local storage helpers
├── pages/              # Top-level page components
│   └── ErrorPage.tsx          # Error boundary fallback
├── App.tsx             # Main application component with routing
└── main.tsx            # Entry point
```

## Component Details

### Dashboard Components

The dashboard provides an overview of the user's learning progress and quick access to study activities.

- **DashboardPage**: Main container for the dashboard, fetches and coordinates dashboard data
- **LastStudySessionCard**: Displays details of the most recent study session including activity type, group studied, and performance metrics
- **StudyProgressCard**: Visualizes the user's learning progress with charts and percentage indicators
- **QuickStatsCard**: Shows key metrics such as total words learned, streak days, and study time
- **StartStudyingCard**: Prominent CTA component with quick access to start studying

### Group Components

Group components manage collections of related vocabulary words.

- **GroupsPage**: Lists all word groups with filtering and sorting options
- **GroupDetails**: Shows comprehensive view of a group including member words and study statistics
- **GroupCard**: Card representation for groups in listing view with visual indicators for progress
- **AddGroupModal**: Modal dialog for creating new word groups with validation
- **EditGroupModal**: Similar to add modal but pre-populated with existing data for editing

### Layout Components

These components provide the structure and navigation for the application.

- **Navbar**: Top navigation bar with app title, search bar, and navigation links
- **Sidebar**: Side menu for main navigation with collapsible sections
- **MainLayout**: Container component that wraps all pages with consistent layout
- **ErrorBoundary**: Catches and gracefully handles React component errors
- **LoadingSpinner**: Reusable loading indicator with animations

### Search Components

The search functionality allows users to find words, groups, and sessions from anywhere in the app.

- **SearchBar**: Input field for search queries with autocomplete suggestions
- **SearchResults**: Displays categorized search results with highlighting
- **SearchResultItem**: Individual search result with appropriate details and navigation
- **SearchFilters**: Allows filtering search results by type, date, and other criteria

### Settings Components

Settings components allow users to customize their learning experience.

- **SettingsPage**: Central location for all user preferences and settings
- **ThemeToggle**: Switch between light and dark theme modes
- **LanguageSelector**: Change the UI language (for future localization)
- **ResetButton**: Reset application state or clear specific data

### Study Components

Study components facilitate the learning process through various activities.

- **ActivitySelector**: Interface for choosing which type of study activity to engage in
- **SessionSummary**: Displays results and statistics after completing a study session
- **StudyHeader**: Shows context information during study (group name, progress)
- **StudyControls**: Navigation buttons for moving through study items
- **Timer**: Tracks and displays time spent during study sessions

#### Study Activity Components

Each activity type has specialized components:

- **FlashcardActivity**: Traditional flashcard study with front/back flipping
  - **Flashcard**: Individual card with word and translation
  - **FlashcardControls**: Buttons for revealing answer and indicating knowledge level
  
- **MatchingActivity**: Matching game where users connect words with translations
  - **MatchingCard**: Interactive card for the matching game
  - **MatchingBoard**: Grid layout for the matching game with state management
  
- **MultipleChoiceActivity**: Quiz-style activity with questions and options
  - **Question**: Displays the word or phrase to be identified
  - **AnswerOptions**: Shows multiple choices with selection handling
  
- **TypingActivity**: Test recall by typing the correct translation
  - **TypingPrompt**: Displays the word requiring translation
  - **TypingInput**: Text input with real-time validation and feedback

### Word Components

Word components manage individual vocabulary items.

- **WordsPage**: Lists all vocabulary words with search, filter, and sort capabilities
- **WordDetails**: Comprehensive view of a word with meanings, examples, and study statistics
- **WordCard**: Card representation for words in listing view
- **AddWordModal**: Modal dialog for adding new vocabulary words
- **EditWordModal**: Modal for editing existing words
- **WordForm**: Reusable form for word data entry with validation
- **JapaneseWordDisplay**: Specialized component to display Japanese words with furigana readings

### UI Components

Reusable UI components that implement the design system.

- **Button**: Customizable button with variants (primary, secondary, text, icon)
- **Card**: Container component with consistent styling and optional features
- **Modal**: Dialog component for forms and confirmations
- **TextField**: Text input with validation, hints, and error states
- **Dropdown**: Select component for choosing from options
- **ProgressBar**: Visual indicator of progress or completion
- **Tag**: Small label component for categories or status indicators
- **Alert**: Notification component for success, error, info messages
- **Tooltip**: Information popup for additional context
- **Charts**: Visualization components for data representation
  - **BarChart**: Horizontal or vertical bar charts
  - **LineChart**: Line graphs for tracking progress over time
  - **PieChart**: Circular charts for showing proportions

## Data Flow Architecture

The application uses a unidirectional data flow pattern:

1. **State Management**: React Context API provides global state
2. **Service Layer**: API services fetch and process data
3. **Component Hierarchy**: Parent components pass props down to children
4. **Event Handlers**: Child components emit events captured by parents

### API Integration

Components interact with backend data through the API service layer:

```tsx
// Example of a component using the API service
function WordsPage() {
  const [words, setWords] = useState<Word[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchWords = async () => {
      try {
        setLoading(true);
        const data = await wordService.getAllWords();
        setWords(data);
      } catch (err) {
        setError('Failed to load words');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchWords();
  }, []);

  // Component rendering logic...
}
```

## State Management

The application uses a combination of:

- **React Context API** for application-wide state
  - **SearchContext**: Manages search queries and results
  - **SettingsContext**: Stores user preferences
  - **ThemeContext**: Handles theme switching
  
- **Component-local state** with `useState` for component-specific state
  - Form inputs
  - UI toggle states
  - Component-specific loading states
  
- **URL parameters** via React Router for navigation state
  - Current view/page
  - Selected item IDs
  - Filter parameters

## Key Features

1. **Dashboard**
   - Overview of learning progress
   - Recent activity summary
   - Quick stats and learning metrics
   - Direct access to study features

2. **Study Activities**
   - **Flashcards**: Traditional flashcard study with spaced repetition
   - **Multiple Choice**: Test comprehension with multiple choice questions
   - **Typing Practice**: Improve recall by typing translations
   - **Matching Game**: Pair words and translations in an interactive game

3. **Word Management**
   - Browse and search vocabulary
   - View detailed word information
   - See study statistics for each word
   - Add, edit, and delete words

4. **Group System**
   - Organize words into thematic groups
   - Study specific word collections
   - Track progress by group
   - Manage group membership

5. **Study Sessions**
   - Record of all study activity
   - Performance metrics and analysis
   - Review past sessions
   - Track improvement over time

6. **Global Search**
   - Search across words, groups, and sessions
   - Quick access to content from anywhere in the app
   - Advanced filtering options
   - Highlighted search results

7. **Settings**
   - Customize the learning experience
   - Set preferences for study activities
   - Theme selection
   - Data management

## Styling

- Uses the **Nord** color palette for a cohesive, modern aesthetic
- Responsive design that works across devices
- Component-based styling with styled-components
- Consistent spacing and typography system

### Theme Structure

```ts
const theme = {
  colors: {
    primary: '#5E81AC',
    secondary: '#81A1C1',
    accent: '#88C0D0',
    success: '#A3BE8C',
    warning: '#EBCB8B',
    error: '#BF616A',
    info: '#B48EAD',
    background: {
      light: '#ECEFF4',
      main: '#E5E9F0',
      dark: '#D8DEE9'
    },
    text: {
      primary: '#2E3440',
      secondary: '#3B4252',
      disabled: '#4C566A'
    }
  },
  shadows: {
    sm: '0 1px 2px rgba(46, 52, 64, 0.1)',
    md: '0 2px 4px rgba(46, 52, 64, 0.1)',
    lg: '0 4px 8px rgba(46, 52, 64, 0.1)'
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    xxl: '3rem'
  },
  typography: {
    fontFamily: "'Inter', 'Noto Sans JP', sans-serif",
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      md: '1rem',
      lg: '1.25rem',
      xl: '1.5rem',
      xxl: '2rem'
    }
  },
  borderRadius: {
    sm: '0.25rem',
    md: '0.5rem',
    lg: '1rem',
    full: '9999px'
  },
  transition: {
    fast: '150ms ease-in-out',
    normal: '250ms ease-in-out',
    slow: '350ms ease-in-out'
  }
};
```

## Responsive Design

The application is fully responsive with specific layouts for:

- Mobile devices (320px-768px)
- Tablets (769px-1024px)
- Desktops (1025px-1440px)
- Large screens (1441px+)

Media queries are organized in a dedicated file for consistency:

```ts
// mediaQueries.ts
export const breakpoints = {
  mobile: 768,
  tablet: 1024,
  desktop: 1440
};

export const media = {
  mobile: `@media (max-width: ${breakpoints.mobile}px)`,
  tablet: `@media (min-width: ${breakpoints.mobile + 1}px) and (max-width: ${breakpoints.tablet}px)`,
  desktop: `@media (min-width: ${breakpoints.tablet + 1}px)`,
  largeDesktop: `@media (min-width: ${breakpoints.desktop + 1}px)`
};
```

## Development

### Prerequisites

- Node.js (v14+)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Start the development server:
```bash
npm run dev
# or
yarn dev
```

3. Open your browser and visit: `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build for production
- `npm run preview` - Preview the production build
- `npm run lint` - Lint the codebase
- `npm run format` - Format code with Prettier

### Best Practices

1. **Component Organization**
   - One component per file
   - Use index.ts files for clean imports
   - Group related components in directories
   - Follow the container/presentation pattern for complex components

2. **Styling**
   - Use styled-components
   - Keep styled component definitions at the top of the file
   - Use the theme for consistent styling
   - Create reusable style blocks for common patterns

3. **State Management**
   - Use contexts for shared state
   - Keep component state minimal and focused
   - Avoid prop drilling more than 2-3 levels
   - Consider custom hooks for complex state logic

4. **Performance**
   - Use React.memo for expensive components
   - Use useCallback and useMemo appropriately
   - Implement virtualization for long lists
   - Lazy load components for code splitting

5. **API Calls**
   - Use the API service layer
   - Handle loading and error states
   - Implement proper data caching
   - Use AbortController for cancelable requests

## Mock Data

During development, the application uses mock data provided by the `mockService.ts` file. This allows for development without a backend dependency. The mock service simulates API delays and provides realistic data structures.

Example of mock data generation:

```ts
// Sample from mockService.ts
export const mockWords: Word[] = [
  {
    id: 1,
    japanese: '猫',
    romaji: 'neko',
    english: 'cat',
    notes: 'Common household pet',
    difficulty: 1,
    created_at: '2023-01-15T10:30:00Z',
    updated_at: '2023-01-15T10:30:00Z'
  },
  // More mock words...
];

export const getWords = async (): Promise<Word[]> => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  return [...mockWords];
};
```

## Deployment

To deploy the application:

1. Build the production version:
```bash
npm run build
# or
yarn build
```

2. The output will be in the `dist` directory, which can be served by any static file server.

### Deployment Options

- **Static Hosting**: Netlify, Vercel, GitHub Pages
- **Container-Based**: Docker with Nginx
- **Traditional Hosting**: Apache or Nginx on VPS

## Contributing

For contribution guidelines, please see the root [CONTRIBUTING.md](../CONTRIBUTING.md) file. 