package service

import (
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/repository"
)

// DashboardService handles dashboard-related business logic
type DashboardService struct {
	wordRepo        *repository.WordRepository
	groupRepo       *repository.GroupRepository
	studySessionRepo *repository.StudySessionRepository
	
	// Add this field to explicitly use the models package
	sessionType     *models.StudySession
}

// NewDashboardService creates a new dashboard service
func NewDashboardService(
	wordRepo *repository.WordRepository,
	groupRepo *repository.GroupRepository,
	studySessionRepo *repository.StudySessionRepository,
) *DashboardService {
	return &DashboardService{
		wordRepo:        wordRepo,
		groupRepo:       groupRepo,
		studySessionRepo: studySessionRepo,
		sessionType:     nil, // Just to use the models package
	}
}

// LastStudySession represents the last study session data for the dashboard
type LastStudySession struct {
	ID        int    `json:"id"`
	GroupID   int    `json:"group_id"`
	GroupName string `json:"group_name"`
	Date      string `json:"date"`
	Score     int    `json:"score"`
	Total     int    `json:"total"`
}

// StudyProgress represents the study progress data for the dashboard
type StudyProgress struct {
	TotalWords      int `json:"total_words"`
	WordsStudied    int `json:"words_studied"`
	WordsMastered   int `json:"words_mastered"`
	CompletionRate  int `json:"completion_rate"`
}

// QuickStats represents quick statistics for the dashboard
type QuickStats struct {
	TotalGroups     int `json:"total_groups"`
	TotalWords      int `json:"total_words"`
	TotalSessions   int `json:"total_sessions"`
	AverageScore    int `json:"average_score"`
}

// GetLastStudySession returns the most recent study session
func (s *DashboardService) GetLastStudySession() (*LastStudySession, error) {
	session, err := s.studySessionRepo.GetLastSession()
	if err != nil {
		return nil, err
	}
	
	// Get group name
	group, err := s.groupRepo.GetGroupByID(session.GroupID)
	if err != nil {
		// If we can't get the group, still return session with a placeholder
		return &LastStudySession{
			ID:        session.ID,
			GroupID:   session.GroupID,
			GroupName: "Unknown Group",
			Date:      session.CreatedAt.Format("2006-01-02 15:04:05"),
			Score:     session.Score,
			Total:     session.Total,
		}, nil
	}
	
	return &LastStudySession{
		ID:        session.ID,
		GroupID:   session.GroupID,
		GroupName: group.Name,
		Date:      session.CreatedAt.Format("2006-01-02 15:04:05"),
		Score:     session.Score,
		Total:     session.Total,
	}, nil
}

// GetStudyProgress returns the user's study progress
func (s *DashboardService) GetStudyProgress() (*StudyProgress, error) {
	totalWords, err := s.wordRepo.CountWords()
	if err != nil {
		return nil, err
	}
	
	wordsStudied, err := s.wordRepo.CountWordsStudied()
	if err != nil {
		return nil, err
	}
	
	wordsMastered, err := s.wordRepo.CountWordsMastered()
	if err != nil {
		return nil, err
	}
	
	var completionRate int
	if totalWords > 0 {
		completionRate = (wordsMastered * 100) / totalWords
	}
	
	return &StudyProgress{
		TotalWords:     totalWords,
		WordsStudied:   wordsStudied,
		WordsMastered:  wordsMastered,
		CompletionRate: completionRate,
	}, nil
}

// GetQuickStats returns quick statistics for the dashboard
func (s *DashboardService) GetQuickStats() (*QuickStats, error) {
	totalGroups, err := s.groupRepo.CountGroups()
	if err != nil {
		return nil, err
	}
	
	totalWords, err := s.wordRepo.CountWords()
	if err != nil {
		return nil, err
	}
	
	totalSessions, err := s.studySessionRepo.CountSessions()
	if err != nil {
		return nil, err
	}
	
	averageScore, err := s.studySessionRepo.GetAverageScore()
	if err != nil {
		return nil, err
	}
	
	return &QuickStats{
		TotalGroups:   totalGroups,
		TotalWords:    totalWords,
		TotalSessions: totalSessions,
		AverageScore:  averageScore,
	}, nil
}

// CountTotalWords returns the total number of words in the database
func CountTotalWords() (int, error) {
	var count int
	query := "SELECT COUNT(*) FROM words"
	err := db.QueryRow(query).Scan(&count)
	if err != nil {
		return 0, err
	}
	return count, nil
}

// CountWordsStudied returns the number of words that have been studied at least once
func CountWordsStudied() (int, error) {
	var count int
	query := "SELECT COUNT(*) FROM words WHERE correct_count > 0 OR wrong_count > 0"
	err := db.QueryRow(query).Scan(&count)
	if err != nil {
		return 0, err
	}
	return count, nil
}

// CountWordsMastered returns the number of words that have been mastered
// A word is considered mastered if it has been answered correctly more times than incorrectly
// and has been studied at least 3 times
func CountWordsMastered() (int, error) {
	var count int
	query := `SELECT COUNT(*) FROM words 
              WHERE correct_count > wrong_count 
              AND (correct_count + wrong_count) >= 3`
	err := db.QueryRow(query).Scan(&count)
	if err != nil {
		return 0, err
	}
	return count, nil
}

// CountTotalGroups returns the total number of word groups
func CountTotalGroups() (int, error) {
	var count int
	query := "SELECT COUNT(*) FROM groups"
	err := db.QueryRow(query).Scan(&count)
	if err != nil {
		return 0, err
	}
	return count, nil
}

// CountTotalSessions returns the total number of study sessions
func CountTotalSessions() (int, error) {
	var count int
	query := "SELECT COUNT(*) FROM study_sessions"
	err := db.QueryRow(query).Scan(&count)
	if err != nil {
		return 0, err
	}
	return count, nil
}

// CalculateAverageScore calculates the average score across all study sessions
func CalculateAverageScore() (int, error) {
	var average float64
	query := `SELECT CASE WHEN COUNT(*) = 0 THEN 0 
              ELSE ROUND(AVG(CAST(score AS FLOAT) / CAST(total AS FLOAT) * 100)) 
              END AS average_score
              FROM study_sessions`
	
	err := db.QueryRow(query).Scan(&average)
	if err != nil {
		return 0, err
	}
	
	return int(average), nil
} 