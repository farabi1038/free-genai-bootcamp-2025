package service

import (
	"database/sql"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
)

// WordService handles business logic for words
type WordService struct {
	db *sql.DB
}

// NewWordService creates a new word service
func NewWordService(db *sql.DB) *WordService {
	return &WordService{db: db}
}

// GetAllWords returns all words
func (s *WordService) GetAllWords() ([]models.Word, error) {
	return models.GetAllWords(s.db)
}

// GetWordsByGroupID returns all words in a group
func (s *WordService) GetWordsByGroupID(groupID int) ([]models.Word, error) {
	return models.GetWordsByGroupID(s.db, groupID)
}

// GetWordByID returns a single word by ID
func (s *WordService) GetWordByID(id int) (*models.Word, error) {
	return models.GetWordByID(s.db, id)
} 