package models

import (
	"database/sql"
	"time"
)

// StudySession represents a study session record
type StudySession struct {
	ID              int       `json:"id"`
	GroupID         int       `json:"group_id"`
	CreatedAt       time.Time `json:"created_at"`
	StudyActivityID int       `json:"study_activity_id"`
	GroupName       string    `json:"group_name,omitempty"`
}

// CreateStudySession creates a new study session in the database
func CreateStudySession(db *sql.DB, groupID, studyActivityID int) (*StudySession, error) {
	query := `INSERT INTO study_sessions (group_id, created_at, study_activity_id) VALUES (?, ?, ?)`
	now := time.Now()
	result, err := db.Exec(query, groupID, now, studyActivityID)
	if err != nil {
		return nil, err
	}
	
	id, err := result.LastInsertId()
	if err != nil {
		return nil, err
	}
	
	return &StudySession{
		ID:              int(id),
		GroupID:         groupID,
		CreatedAt:       now,
		StudyActivityID: studyActivityID,
	}, nil
}

// GetLastStudySession retrieves the most recent study session
func GetLastStudySession(db *sql.DB) (*StudySession, error) {
	query := `
		SELECT s.id, s.group_id, s.created_at, s.study_activity_id, g.name 
		FROM study_sessions s
		JOIN groups g ON s.group_id = g.id
		ORDER BY s.created_at DESC 
		LIMIT 1
	`
	
	var session StudySession
	var createdAt string
	
	err := db.QueryRow(query).Scan(
		&session.ID, 
		&session.GroupID, 
		&createdAt, 
		&session.StudyActivityID,
		&session.GroupName,
	)
	
	if err != nil {
		return nil, err
	}
	
	// Parse the time string
	session.CreatedAt, err = time.Parse(time.RFC3339, createdAt)
	if err != nil {
		return nil, err
	}
	
	return &session, nil
}

// CountTotalStudiedWords counts the total number of unique words studied
func CountTotalStudiedWords(db *sql.DB) (int, error) {
	query := `
		SELECT COUNT(DISTINCT word_id) 
		FROM words_studied
	`
	
	var count int
	err := db.QueryRow(query).Scan(&count)
	if err != nil {
		return 0, err
	}
	
	return count, nil
}

// CountTotalAvailableWords counts the total number of words in the database
func CountTotalAvailableWords(db *sql.DB) (int, error) {
	query := `SELECT COUNT(*) FROM words`
	
	var count int
	err := db.QueryRow(query).Scan(&count)
	if err != nil {
		return 0, err
	}
	
	return count, nil
}

// ResetStudyHistory removes all study session records
func ResetStudyHistory(db *sql.DB) error {
	query := `DELETE FROM study_sessions`
	_, err := db.Exec(query)
	return err
} 