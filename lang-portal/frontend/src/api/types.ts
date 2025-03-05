// Common interfaces for API responses

export interface ApiSuccessResponse<T> {
  success: true;
  data: T;
}

export interface ApiErrorResponse {
  success: false;
  error: {
    message: string;
    status: number;
    details?: any;
  };
}

export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

// Domain-specific interfaces

export interface Word {
  id: string;
  japanese: string;
  romaji: string;
  english: string;
  correct_count: number;
  wrong_count: number;
}

export interface Group {
  id: string;
  name: string;
  word_count: number;
}

export interface StudyActivity {
  id: string;
  name: string;
  description: string;
  thumbnail_url: string;
  url: string;
}

export interface StudySession {
  id: string;
  activity_name: string;
  group_id: string;
  group_name: string;
  start_time: string;
  end_time: string;
  review_item_count: number;
  correct_count: number;
  wrong_count: number;
}

export interface WordResult {
  word_id: string;
  japanese: string;
  romaji: string;
  english: string;
  is_correct: boolean;
  response_time_ms: number;
}

export interface StudySessionDetail extends StudySession {
  word_results: WordResult[];
  accuracy_percentage: number;
  average_response_time_ms: number;
}

export interface LastStudySession {
  activity: string;
  timestamp: string;
  correct: number;
  wrong: number;
  group: string;
  group_id: string;
}

export interface StudyProgress {
  wordsStudied: number;
  totalWords: number;
  masteryRate: number;
}

export interface QuickStats {
  successRate: number;
  totalSessions: number;
  activeGroups: number;
  streak: number;
}

export interface ActivityType {
  id: string;
  name: string;
  description: string;
  icon: string;
  benefits: string[];
  recommendedFor: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  instructions: string;
} 