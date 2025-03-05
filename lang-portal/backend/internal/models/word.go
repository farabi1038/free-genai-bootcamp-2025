package models

import (
	"database/sql"
	"time"
	"log"
	"errors"
)

// GetAllWords retrieves all words from the database
func GetAllWords(db *sql.DB) ([]Word, error) {
	query := `SELECT id, japanese, romaji, english, correct_count, wrong_count, created_at, updated_at FROM words`
	rows, err := db.Query(query)
	if err != nil {
		log.Printf("Error querying all words: %v", err)
		return nil, err
	}
	defer rows.Close()

	var words []Word
	for rows.Next() {
		var word Word
		var createdAt, updatedAt string
		err := rows.Scan(
			&word.ID,
			&word.Japanese,
			&word.Romaji,
			&word.English,
			&word.CorrectCount,
			&word.WrongCount,
			&createdAt,
			&updatedAt,
		)
		if err != nil {
			log.Printf("Error scanning word row: %v", err)
			return nil, err
		}

		// Parse timestamps
		word.CreatedAt, _ = time.Parse("2006-01-02 15:04:05", createdAt)
		word.UpdatedAt, _ = time.Parse("2006-01-02 15:04:05", updatedAt)

		words = append(words, word)
	}

	if err = rows.Err(); err != nil {
		log.Printf("Error iterating word rows: %v", err)
		return nil, err
	}

	return words, nil
}

// GetWords retrieves words with pagination and optional search
func GetWords(db *sql.DB, page, limit int, search string) ([]Word, int, error) {
	if db == nil {
		return nil, 0, errors.New("database connection is nil")
	}

	var countQuery string
	var dataQuery string
	var args []interface{}
	
	offset := (page - 1) * limit
	
	if search != "" {
		// If search is provided, add a WHERE clause for search
		searchPattern := "%" + search + "%"
		countQuery = `
			SELECT COUNT(*) FROM words 
			WHERE japanese LIKE ? OR romaji LIKE ? OR english LIKE ?
		`
		dataQuery = `
			SELECT id, japanese, romaji, english, correct_count, wrong_count, created_at, updated_at FROM words 
			WHERE japanese LIKE ? OR romaji LIKE ? OR english LIKE ?
			LIMIT ? OFFSET ?
		`
		args = append(args, searchPattern, searchPattern, searchPattern, limit, offset)
	} else {
		// If no search is provided, fetch all words with pagination
		countQuery = `SELECT COUNT(*) FROM words`
		dataQuery = `
			SELECT id, japanese, romaji, english, correct_count, wrong_count, created_at, updated_at FROM words 
			FROM words LIMIT ? OFFSET ?
		`
		args = append(args, limit, offset)
	}
	
	// Get total count - handle the case when no search arguments
	var totalCount int
	var countErr error
	if search != "" {
		countErr = db.QueryRow(countQuery, args[0], args[1], args[2]).Scan(&totalCount)
	} else {
		countErr = db.QueryRow(countQuery).Scan(&totalCount)
	}
	
	if countErr != nil {
		log.Printf("Error getting count: %v", countErr)
		return nil, 0, countErr
	}
	
	// Get paginated data
	rows, err := db.Query(dataQuery, args...)
	if err != nil {
		log.Printf("Error querying words with pagination: %v", err)
		return nil, 0, err
	}
	defer rows.Close()
	
	var words []Word
	for rows.Next() {
		var word Word
		var createdAt, updatedAt string
		if err := rows.Scan(&word.ID, &word.Japanese, &word.Romaji, &word.English, &word.CorrectCount, &word.WrongCount, &createdAt, &updatedAt); err != nil {
			log.Printf("Error scanning paginated word row: %v", err)
			return nil, 0, err
		}

		// Parse timestamps
		word.CreatedAt, _ = time.Parse("2006-01-02 15:04:05", createdAt)
		word.UpdatedAt, _ = time.Parse("2006-01-02 15:04:05", updatedAt)

		words = append(words, word)
	}
	
	if err = rows.Err(); err != nil {
		log.Printf("Error after scanning all rows: %v", err)
		return nil, 0, err
	}
	
	return words, totalCount, nil
}

// GetWordsByGroupID retrieves all words belonging to a specific group
func GetWordsByGroupID(db *sql.DB, groupID int) ([]Word, error) {
	query := `
		SELECT w.id, w.japanese, w.romaji, w.english, w.correct_count, w.wrong_count, w.created_at, w.updated_at 
		FROM words w 
		JOIN word_groups wg ON w.id = wg.word_id 
		WHERE wg.group_id = ?
	`
	rows, err := db.Query(query, groupID)
	if err != nil {
		log.Printf("Error querying words by group ID: %v", err)
		return nil, err
	}
	defer rows.Close()

	var words []Word
	for rows.Next() {
		var word Word
		var createdAt, updatedAt string
		if err := rows.Scan(&word.ID, &word.Japanese, &word.Romaji, &word.English, &word.CorrectCount, &word.WrongCount, &createdAt, &updatedAt); err != nil {
			log.Printf("Error scanning group word row: %v", err)
			return nil, err
		}

		// Parse timestamps
		word.CreatedAt, _ = time.Parse("2006-01-02 15:04:05", createdAt)
		word.UpdatedAt, _ = time.Parse("2006-01-02 15:04:05", updatedAt)

		words = append(words, word)
	}

	return words, nil
}

// GetWordByID retrieves a single word by its ID
func GetWordByID(db *sql.DB, id int) (*Word, error) {
	query := `SELECT id, japanese, romaji, english, correct_count, wrong_count, created_at, updated_at FROM words WHERE id = ?`
	
	var word Word
	var createdAt, updatedAt string
	
	err := db.QueryRow(query, id).Scan(
		&word.ID,
		&word.Japanese,
		&word.Romaji,
		&word.English,
		&word.CorrectCount,
		&word.WrongCount,
		&createdAt,
		&updatedAt,
	)
	
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}
	
	// Parse timestamps
	word.CreatedAt, _ = time.Parse("2006-01-02 15:04:05", createdAt)
	word.UpdatedAt, _ = time.Parse("2006-01-02 15:04:05", updatedAt)
	
	// Get groups for this word
	groupQuery := `
		SELECT g.name
		FROM groups g
		JOIN group_words gw ON g.id = gw.group_id
		WHERE gw.word_id = ?
	`
	
	groupRows, err := db.Query(groupQuery, id)
	if err != nil {
		return nil, err
	}
	defer groupRows.Close()
	
	var groups []string
	for groupRows.Next() {
		var groupName string
		if err := groupRows.Scan(&groupName); err != nil {
			return nil, err
		}
		groups = append(groups, groupName)
	}
	
	if err = groupRows.Err(); err != nil {
		return nil, err
	}
	
	word.Groups = groups
	
	return &word, nil
}

// CreateWord adds a new word to the database
func CreateWord(db *sql.DB, japanese, romaji, english string) (*Word, error) {
	query := `INSERT INTO words (japanese, romaji, english, correct_count, wrong_count) VALUES (?, ?, ?, 0, 0)`
	result, err := db.Exec(query, japanese, romaji, english)
	if err != nil {
		return nil, err
	}
	
	id, err := result.LastInsertId()
	if err != nil {
		return nil, err
	}
	
	return &Word{
		ID:           int(id),
		Japanese:     japanese,
		Romaji:       romaji,
		English:      english,
		CorrectCount: 0,
		WrongCount:   0,
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}, nil
}

// UpdateWordStats updates the correct and wrong counts for a word
func UpdateWordStats(db *sql.DB, wordID int, isCorrect bool) error {
	var query string
	if isCorrect {
		query = `UPDATE words SET correct_count = correct_count + 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?`
	} else {
		query = `UPDATE words SET wrong_count = wrong_count + 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?`
	}
	
	_, err := db.Exec(query, wordID)
	return err
} 