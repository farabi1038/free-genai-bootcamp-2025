package service

import (
	"database/sql"

	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
)

// GetAllStudySessions retrieves all study sessions with pagination
func GetAllStudySessions(page, limit int) ([]models.StudySessionResponse, error) {
	offset := (page - 1) * limit
	
	query := `SELECT s.id, s.group_id, g.name as group_name, s.activity_id, 
              a.name as activity_name, s.score, s.total, s.created_at
              FROM study_sessions s
              JOIN groups g ON s.group_id = g.id
              JOIN study_activities a ON s.activity_id = a.id
              ORDER BY s.created_at DESC
              LIMIT ? OFFSET ?`
	
	rows, err := db.Query(query, limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var sessions []models.StudySessionResponse
	for rows.Next() {
		var session models.StudySessionResponse
		err := rows.Scan(
			&session.ID,
			&session.GroupID,
			&session.GroupName,
			&session.ActivityID,
			&session.ActivityName,
			&session.Score,
			&session.Total,
			&session.CreatedAt,
		)
		if err != nil {
			return nil, err
		}
		sessions = append(sessions, session)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	return sessions, nil
}

// GetStudySessionByIDWithDetails retrieves a study session by ID with group and activity details
func GetStudySessionByIDWithDetails(id int) (*models.StudySessionResponse, error) {
	query := `SELECT s.id, s.group_id, g.name as group_name, s.activity_id, 
              a.name as activity_name, s.score, s.total, s.created_at
              FROM study_sessions s
              JOIN groups g ON s.group_id = g.id
              JOIN study_activities a ON s.activity_id = a.id
              WHERE s.id = ?`
	
	var session models.StudySessionResponse
	err := db.QueryRow(query, id).Scan(
		&session.ID,
		&session.GroupID,
		&session.GroupName,
		&session.ActivityID,
		&session.ActivityName,
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

// GetStudyRecordsBySessionID retrieves study records for a specific session
func GetStudyRecordsBySessionID(sessionID int) ([]models.StudyRecordWithWord, error) {
	query := `SELECT sr.id, sr.word_id, w.japanese, w.romaji, w.english, 
              sr.correct, sr.created_at
              FROM study_records sr
              JOIN words w ON sr.word_id = w.id
              WHERE sr.session_id = ?
              ORDER BY sr.created_at ASC`
	
	rows, err := db.Query(query, sessionID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var records []models.StudyRecordWithWord
	for rows.Next() {
		var record models.StudyRecordWithWord
		err := rows.Scan(
			&record.ID,
			&record.WordID,
			&record.Japanese,
			&record.Romaji,
			&record.English,
			&record.Correct,
			&record.CreatedAt,
		)
		if err != nil {
			return nil, err
		}
		records = append(records, record)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	return records, nil
} 