package service

import (
	"database/sql"
	"time"

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

// GetWords returns paginated words with optional search
func (s *WordService) GetWords(page int, limit int, search string) ([]models.Word, int, error) {
	return models.GetWords(s.db, page, limit, search)
}

// GetAllWords retrieves all words with pagination
func (s *WordService) GetAllWords(page, limit int) ([]models.Word, error) {
	offset := (page - 1) * limit
	query := `
		SELECT id, japanese, romaji, english
		FROM words
		ORDER BY id
		LIMIT ? OFFSET ?
	`
	
	rows, err := s.db.Query(query, limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	var words []models.Word
	for rows.Next() {
		var word models.Word
		if err := rows.Scan(
			&word.ID,
			&word.Japanese,
			&word.Romaji,
			&word.English,
		); err != nil {
			return nil, err
		}
		// Set default values for stats and timestamps
		word.CorrectCount = 0
		word.WrongCount = 0
		word.CreatedAt = time.Now()
		word.UpdatedAt = time.Now()
		words = append(words, word)
	}
	
	if err = rows.Err(); err != nil {
		return nil, err
	}
	
	return words, nil
}

// GetWordByID retrieves a word by ID
func (s *WordService) GetWordByID(id int) (*models.Word, error) {
	query := `SELECT id, japanese, romaji, english
              FROM words
              WHERE id = ?`
	
	var word models.Word
	err := s.db.QueryRow(query, id).Scan(
		&word.ID,
		&word.Japanese,
		&word.Romaji,
		&word.English,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}

	if err != nil {
		return nil, err
	}

	// Set default values for stats and timestamps
	word.CorrectCount = 0
	word.WrongCount = 0
	word.CreatedAt = time.Now()
	word.UpdatedAt = time.Now()

	return &word, nil
}

// GetWordByIDWithGroups retrieves a word by ID including its associated groups
func (s *WordService) GetWordByIDWithGroups(id int) (*models.WordWithGroups, error) {
	// First get the word
	word, err := s.GetWordByID(id)
	if err != nil {
		return nil, err
	}

	if word == nil {
		return nil, nil
	}

	// Then get its associated groups
	query := `SELECT g.id, g.name, g.created_at, g.updated_at
              FROM groups g
              JOIN group_words gw ON g.id = gw.group_id
              WHERE gw.word_id = ?`
	
	rows, err := s.db.Query(query, id)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var groups []models.Group
	for rows.Next() {
		var group models.Group
		err := rows.Scan(
			&group.ID,
			&group.Name,
			&group.CreatedAt,
			&group.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		groups = append(groups, group)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	// Combine word and groups
	wordWithGroups := &models.WordWithGroups{
		Word:   *word,
		Groups: groups,
	}

	return wordWithGroups, nil
}

// CreateWord creates a new word
func (s *WordService) CreateWord(word *models.Word) error {
	// Set created and updated times
	now := time.Now()
	word.CreatedAt = now
	word.UpdatedAt = now
	
	// Initialize correct and wrong counts to zero
	word.CorrectCount = 0
	word.WrongCount = 0

	query := `
		INSERT INTO words (japanese, romaji, english, correct_count, wrong_count, created_at, updated_at)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	`
	
	result, err := s.db.Exec(
		query,
		word.Japanese,
		word.Romaji,
		word.English,
		word.CorrectCount,
		word.WrongCount,
		word.CreatedAt,
		word.UpdatedAt,
	)
	if err != nil {
		return err
	}
	
	id, err := result.LastInsertId()
	if err != nil {
		return err
	}
	
	word.ID = int(id)
	return nil
}

// GetWordsByGroupID returns all words in a group
func (s *WordService) GetWordsByGroupID(groupID int) ([]models.Word, error) {
	return models.GetWordsByGroupID(s.db, groupID)
}

// AddWordToGroup adds a word to a group
func (s *WordService) AddWordToGroup(wordID, groupID int) error {
	// Check if the word is already in the group
	var count int
	err := s.db.QueryRow("SELECT COUNT(*) FROM group_words WHERE group_id = ? AND word_id = ?", groupID, wordID).Scan(&count)
	if err != nil {
		return err
	}

	// If already exists, do nothing
	if count > 0 {
		return nil
	}

	// Add the word to the group
	_, err = s.db.Exec("INSERT INTO group_words (group_id, word_id) VALUES (?, ?)", groupID, wordID)
	return err
}

// RemoveWordFromGroup removes a word from a group
func (s *WordService) RemoveWordFromGroup(wordID, groupID int) error {
	_, err := s.db.Exec("DELETE FROM group_words WHERE group_id = ? AND word_id = ?", groupID, wordID)
	return err
} 