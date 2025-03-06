package service

import (
	"database/sql"
	"time"

	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
)

// GetStudySessionByID retrieves a study session by its ID
func GetStudySessionByID(id int) (*models.StudySession, error) {
	query := `SELECT id, group_id, activity_id, score, total, created_at 
              FROM study_sessions 
              WHERE id = ?`
	
	var session models.StudySession
	err := db.QueryRow(query, id).Scan(
		&session.ID,
		&session.GroupID,
		&session.ActivityID,
		&session.Score,
		&session.Total,
		&session.CreatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}

	if err != nil {
		return nil, err
	}

	return &session, nil
}

// CompleteStudySession updates a session with final score and returns the updated session
func CompleteStudySession(session *models.StudySession) (*models.StudySession, error) {
	// Set the creation time if not already set
	if session.CreatedAt.IsZero() {
		session.CreatedAt = time.Now()
	}

	query := `INSERT INTO study_sessions (group_id, activity_id, score, total, created_at)
              VALUES (?, ?, ?, ?, ?)`
	
	result, err := db.Exec(
		query,
		session.GroupID,
		session.ActivityID,
		session.Score,
		session.Total,
		session.CreatedAt,
	)
	if err != nil {
		return nil, err
	}

	id, err := result.LastInsertId()
	if err != nil {
		return nil, err
	}

	session.ID = int(id)
	return session, nil
}

// UpdateWordStats updates the correct/wrong count for a word
func UpdateWordStats(wordID int, correct bool) error {
	var updateQuery string
	if correct {
		updateQuery = "UPDATE words SET correct_count = correct_count + 1, updated_at = ? WHERE id = ?"
	} else {
		updateQuery = "UPDATE words SET wrong_count = wrong_count + 1, updated_at = ? WHERE id = ?"
	}

	_, err := db.Exec(updateQuery, time.Now(), wordID)
	return err
}

// RecordStudyActivity records a study activity for a word
func RecordStudyActivity(wordID, sessionID int, correct bool) error {
	query := `INSERT INTO study_records (word_id, session_id, correct, created_at)
              VALUES (?, ?, ?, ?)`
	
	_, err := db.Exec(query, wordID, sessionID, correct, time.Now())
	return err
} 