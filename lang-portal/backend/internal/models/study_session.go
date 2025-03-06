package models

import (
	"database/sql"
	"time"
)

// CreateStudySession creates a new study session in the database
func CreateStudySession(db *sql.DB, groupID, activityID int) (*StudySession, error) {
	query := `INSERT INTO study_sessions (group_id, activity_id, score, total) VALUES (?, ?, 0, 0)`
	result, err := db.Exec(query, groupID, activityID)
	if err != nil {
		return nil, err
	}
	
	id, err := result.LastInsertId()
	if err != nil {
		return nil, err
	}
	
	return &StudySession{
		ID:         int(id),
		GroupID:    groupID,
		ActivityID: activityID,
		Score:      0,
		Total:      0,
		CreatedAt:  time.Now(),
	}, nil
}

// GetLastStudySession retrieves the most recent study session
func GetLastStudySession(db *sql.DB) (*StudySession, error) {
	query := `
		SELECT s.id, s.group_id, s.activity_id, s.score, s.total, s.created_at, g.name 
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
		&session.ActivityID,
		&session.Score,
		&session.Total,
		&createdAt,
		&session.GroupName,
	)
	
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, err
	}
	
	// Parse the timestamp
	session.CreatedAt, err = time.Parse("2006-01-02 15:04:05", createdAt)
	if err != nil {
		return nil, err
	}
	
	return &session, nil
}

// CountTotalStudiedWords returns the count of words that have been studied
func CountTotalStudiedWords(db *sql.DB) (int, error) {
	query := `SELECT COUNT(DISTINCT word_id) FROM study_records`
	var count int
	err := db.QueryRow(query).Scan(&count)
	if err != nil {
		return 0, err
	}
	return count, nil
}

// CountTotalAvailableWords returns the total number of words available for study
func CountTotalAvailableWords(db *sql.DB) (int, error) {
	query := `SELECT COUNT(*) FROM words`
	var count int
	err := db.QueryRow(query).Scan(&count)
	if err != nil {
		return 0, err
	}
	return count, nil
}

// ResetStudyHistory clears all study history
func ResetStudyHistory(db *sql.DB) error {
	tx, err := db.Begin()
	if err != nil {
		return err
	}
	
	_, err = tx.Exec("DELETE FROM study_records")
	if err != nil {
		tx.Rollback()
		return err
	}
	
	_, err = tx.Exec("DELETE FROM study_sessions")
	if err != nil {
		tx.Rollback()
		return err
	}
	
	return tx.Commit()
} 