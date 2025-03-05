package models

import (
	"database/sql"
	"encoding/json"
)

// Word represents a vocabulary word in the database
type Word struct {
	ID       int             `json:"id"`
	Japanese string          `json:"japanese"`
	Romaji   string          `json:"romaji"`
	English  string          `json:"english"`
	Parts    json.RawMessage `json:"parts,omitempty"`
}

// GetAllWords retrieves all words from the database
func GetAllWords(db *sql.DB) ([]Word, error) {
	query := `SELECT id, japanese, romaji, english, parts FROM words`
	rows, err := db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var words []Word
	for rows.Next() {
		var word Word
		var parts []byte
		if err := rows.Scan(&word.ID, &word.Japanese, &word.Romaji, &word.English, &parts); err != nil {
			return nil, err
		}
		if len(parts) > 0 {
			word.Parts = json.RawMessage(parts)
		}
		words = append(words, word)
	}

	return words, nil
}

// GetWordsByGroupID retrieves all words belonging to a specific group
func GetWordsByGroupID(db *sql.DB, groupID int) ([]Word, error) {
	query := `
		SELECT w.id, w.japanese, w.romaji, w.english, w.parts 
		FROM words w 
		JOIN words_groups wg ON w.id = wg.word_id 
		WHERE wg.group_id = ?
	`
	rows, err := db.Query(query, groupID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var words []Word
	for rows.Next() {
		var word Word
		var parts []byte
		if err := rows.Scan(&word.ID, &word.Japanese, &word.Romaji, &word.English, &parts); err != nil {
			return nil, err
		}
		if len(parts) > 0 {
			word.Parts = json.RawMessage(parts)
		}
		words = append(words, word)
	}

	return words, nil
}

// GetWordByID retrieves a single word by its ID
func GetWordByID(db *sql.DB, id int) (*Word, error) {
	query := `SELECT id, japanese, romaji, english, parts FROM words WHERE id = ?`
	var word Word
	var parts []byte
	err := db.QueryRow(query, id).Scan(&word.ID, &word.Japanese, &word.Romaji, &word.English, &parts)
	if err != nil {
		return nil, err
	}
	if len(parts) > 0 {
		word.Parts = json.RawMessage(parts)
	}
	
	return &word, nil
} 