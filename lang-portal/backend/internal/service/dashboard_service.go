package service

import (
	"database/sql"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
)

// DashboardService handles business logic for the dashboard
type DashboardService struct {
	db *sql.DB
}

// NewDashboardService creates a new dashboard service
func NewDashboardService(db *sql.DB) *DashboardService {
	return &DashboardService{db: db}
}

// GetLastStudySession retrieves the most recent study session
func (s *DashboardService) GetLastStudySession() (*models.StudySession, error) {
	return models.GetLastStudySession(s.db)
}

// GetStudyProgress retrieves study progress statistics
func (s *DashboardService) GetStudyProgress() (map[string]int, error) {
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