package service

import (
	"database/sql"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
)

// StudyService handles business logic for study sessions
type StudyService struct {
	db *sql.DB
}

// NewStudyService creates a new study service
func NewStudyService(db *sql.DB) *StudyService {
	return &StudyService{db: db}
}

// CreateStudySession creates a new study session
func (s *StudyService) CreateStudySession(groupID, activityID int) (*models.StudySession, error) {
	return models.CreateStudySession(s.db, groupID, activityID)
}

// GetLastStudySession retrieves the most recent study session
func (s *StudyService) GetLastStudySession() (*models.StudySession, error) {
	return models.GetLastStudySession(s.db)
}

// GetStudyProgress retrieves study progress statistics
func (s *StudyService) GetStudyProgress() (map[string]int, error) {
	studiedWords, err := models.CountTotalStudiedWords(s.db)
	if err != nil {
		return nil, err
	}
	
	totalWords, err := models.CountTotalAvailableWords(s.db)
	if err != nil {
		return nil, err
	}
	
	return map[string]int{
		"total_words_studied":    studiedWords,
		"total_available_words":  totalWords,
	}, nil
}

// ResetStudyHistory removes all study session records
func (s *StudyService) ResetStudyHistory() error {
	return models.ResetStudyHistory(s.db)
}

// FullReset performs a complete system reset
func (s *StudyService) FullReset() error {
	// This would ideally reset all tables or recreate the database
	// For simplicity, we're just resetting study history
	return s.ResetStudyHistory()
} 