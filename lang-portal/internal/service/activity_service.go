package service

import (
	"database/sql"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
)

// ActivityService handles business logic for study activities
type ActivityService struct {
	db *sql.DB
}

// NewActivityService creates a new activity service
func NewActivityService(db *sql.DB) *ActivityService {
	return &ActivityService{db: db}
}

// GetActivityByID returns a single activity by ID
func (s *ActivityService) GetActivityByID(id int) (*models.StudyActivity, error) {
	return models.GetActivityByID(s.db, id)
}

// GetAllActivities returns all available study activities
func (s *ActivityService) GetAllActivities() ([]models.StudyActivity, error) {
	return models.GetAllActivities(s.db)
} 