package service

import (
	"database/sql"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
)

// GroupService handles business logic for word groups
type GroupService struct {
	db *sql.DB
}

// NewGroupService creates a new group service
func NewGroupService(db *sql.DB) *GroupService {
	return &GroupService{db: db}
}

// GetAllGroups returns all word groups
func (s *GroupService) GetAllGroups() ([]models.Group, error) {
	return models.GetAllGroups(s.db)
}

// GetGroupByID returns a single group by ID
func (s *GroupService) GetGroupByID(id int) (*models.Group, error) {
	return models.GetGroupByID(s.db, id)
}

// AddWordToGroup adds a word to a group
func (s *GroupService) AddWordToGroup(wordID, groupID int) error {
	return models.AddWordToGroup(s.db, wordID, groupID)
} 