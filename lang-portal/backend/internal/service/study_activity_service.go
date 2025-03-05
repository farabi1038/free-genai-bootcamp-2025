package service

import (
	"database/sql"
	"time"

	"github.com/free-genai-bootcamp-2025/lang-portal/internal/models"
	"github.com/free-genai-bootcamp-2025/lang-portal/internal/repository"
)

// StudyActivityService handles study sessions and activities
type StudyActivityService struct {
	db *sql.DB
	wordRepo *repository.WordRepository
	groupRepo *repository.GroupRepository
	studySessionRepo *repository.StudySessionRepository
}

// NewStudyActivityService creates a new study activity service
func NewStudyActivityService(
	db *sql.DB,
	wordRepo *repository.WordRepository,
	groupRepo *repository.GroupRepository,
	studySessionRepo *repository.StudySessionRepository,
) *StudyActivityService {
	return &StudyActivityService{
		db: db,
		wordRepo: wordRepo,
		groupRepo: groupRepo,
		studySessionRepo: studySessionRepo,
	}
}

// StudyActivity represents a study activity
type StudyActivity struct {
	ID           int    `json:"id"`
	Name         string `json:"name"`
	Description  string `json:"description"`
	ThumbnailURL string `json:"thumbnail_url"`
	URL          string `json:"url"`
	CreatedAt    string `json:"created_at"`
	UpdatedAt    string `json:"updated_at"`
}

// StudySessionWithDetails represents a study session with additional details
type StudySessionWithDetails struct {
	ID           int    `json:"id"`
	GroupID      int    `json:"group_id"`
	GroupName    string `json:"group_name"`
	ActivityID   int    `json:"activity_id"`
	ActivityName string `json:"activity_name"`
	Score        int    `json:"score"`
	Total        int    `json:"total"`
	CreatedAt    string `json:"created_at"`
}

// WordReview represents a word that was reviewed in a study session
type WordReview struct {
	ID       int    `json:"id"`
	WordID   int    `json:"word_id"`
	Japanese string `json:"japanese"`
	Romaji   string `json:"romaji"`
	English  string `json:"english"`
	Correct  bool   `json:"correct"`
	CreatedAt string `json:"created_at"`
}

// GetAllStudyActivities retrieves all study activities
func (s *StudyActivityService) GetAllStudyActivities() ([]StudyActivity, error) {
	query := `SELECT id, name, description, thumbnail_url, url, created_at, updated_at 
              FROM study_activities 
              ORDER BY name ASC`
	
	rows, err := s.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var activities []StudyActivity
	for rows.Next() {
		var activity StudyActivity
		err := rows.Scan(
			&activity.ID,
			&activity.Name,
			&activity.Description,
			&activity.ThumbnailURL,
			&activity.URL,
			&activity.CreatedAt,
			&activity.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		activities = append(activities, activity)
	}

	if err = rows.Err(); err != nil {
		return nil, err
	}

	return activities, nil
}

// GetStudyActivityByID retrieves a study activity by its ID
func (s *StudyActivityService) GetStudyActivityByID(id int) (*StudyActivity, error) {
	query := `SELECT id, name, description, thumbnail_url, url, created_at, updated_at 
              FROM study_activities 
              WHERE id = ?`
	
	var activity StudyActivity
	err := s.db.QueryRow(query, id).Scan(
		&activity.ID,
		&activity.Name,
		&activity.Description,
		&activity.ThumbnailURL,
		&activity.URL,
		&activity.CreatedAt,
		&activity.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}

	if err != nil {
		return nil, err
	}

	return &activity, nil
}

// GetStudySessionsByActivityID retrieves study sessions for a specific activity
func (s *StudyActivityService) GetStudySessionsByActivityID(activityID int) ([]StudySessionWithDetails, error) {
	query := `SELECT s.id, s.group_id, g.name as group_name, s.activity_id, 
              a.name as activity_name, s.score, s.total, s.created_at
              FROM study_sessions s
              JOIN groups g ON s.group_id = g.id
              JOIN study_activities a ON s.activity_id = a.id
              WHERE s.activity_id = ?
              ORDER BY s.created_at DESC`
	
	rows, err := s.db.Query(query, activityID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var sessions []StudySessionWithDetails
	for rows.Next() {
		var session StudySessionWithDetails
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

// LaunchStudyActivity launches a study activity for a specific group
func (s *StudyActivityService) LaunchStudyActivity(activityID, groupID int) (map[string]interface{}, error) {
	// In a real app, this would create a new study session and return information needed to start the activity
	// For now, we'll just return some data
	
	// Check if the activity exists
	activity, err := s.GetStudyActivityByID(activityID)
	if err != nil {
		return nil, err
	}
	
	if activity == nil {
		return nil, nil
	}
	
	// Check if the group exists
	group, err := s.groupRepo.GetGroupByID(groupID)
	if err != nil {
		return nil, err
	}
	
	if group == nil {
		return nil, nil
	}
	
	// Create a new study session
	session := &models.StudySession{
		GroupID: groupID,
		Score:   0,
		Total:   0,
	}
	
	if err := s.studySessionRepo.CreateStudySession(session); err != nil {
		return nil, err
	}
	
	// Return data needed to start the activity
	return map[string]interface{}{
		"session_id":     session.ID,
		"activity_id":    activityID,
		"activity_name":  activity.Name,
		"activity_url":   activity.URL,
		"group_id":       groupID,
		"group_name":     group.Name,
	}, nil
}

// GetAllStudySessions retrieves all study sessions with pagination
func (s *StudyActivityService) GetAllStudySessions(page, limit int) ([]StudySessionWithDetails, error) {
	// In a real app, this would query the database for all sessions with pagination
	// For now, we'll return mock data
	return []StudySessionWithDetails{
		{
			ID:           1,
			GroupID:      1,
			GroupName:    "Basic Phrases",
			ActivityID:   1,
			ActivityName: "Flashcards",
			Score:        8,
			Total:        10,
			CreatedAt:    "2023-06-15T14:30:00Z",
		},
		{
			ID:           2,
			GroupID:      2,
			GroupName:    "Common Nouns",
			ActivityID:   2,
			ActivityName: "Matching Game",
			Score:        7,
			Total:        10,
			CreatedAt:    "2023-06-16T10:15:00Z",
		},
	}, nil
}

// GetStudySessionByID retrieves a study session by its ID
func (s *StudyActivityService) GetStudySessionByID(id int) (*StudySessionWithDetails, error) {
	// In a real app, this would query the database for the session with the given ID
	// For now, we'll return mock data
	if id == 1 {
		return &StudySessionWithDetails{
			ID:           1,
			GroupID:      1,
			GroupName:    "Basic Phrases",
			ActivityID:   1,
			ActivityName: "Flashcards",
			Score:        8,
			Total:        10,
			CreatedAt:    "2023-06-15T14:30:00Z",
		}, nil
	}
	
	if id == 2 {
		return &StudySessionWithDetails{
			ID:           2,
			GroupID:      2,
			GroupName:    "Common Nouns",
			ActivityID:   2,
			ActivityName: "Matching Game",
			Score:        7,
			Total:        10,
			CreatedAt:    "2023-06-16T10:15:00Z",
		}, nil
	}
	
	return nil, nil
}

// GetStudySessionWords retrieves words reviewed in a specific study session
func (s *StudyActivityService) GetStudySessionWords(sessionID int) ([]WordReview, error) {
	// In a real app, this would query the database for words reviewed in the given session
	// For now, we'll return mock data
	return []WordReview{
		{
			ID:        1,
			WordID:    1,
			Japanese:  "こんにちは",
			Romaji:    "konnichiwa",
			English:   "hello",
			Correct:   true,
			CreatedAt: "2023-06-15T14:30:00Z",
		},
		{
			ID:        2,
			WordID:    2,
			Japanese:  "さようなら",
			Romaji:    "sayounara",
			English:   "goodbye",
			Correct:   false,
			CreatedAt: "2023-06-15T14:31:00Z",
		},
	}, nil
}

// CreateStudySession creates a new study session
func (s *StudyActivityService) CreateStudySession(session *models.StudySession) error {
	return s.studySessionRepo.CreateStudySession(session)
}

// UpdateWordStats updates the correct and wrong counts for a word
func (s *StudyActivityService) UpdateWordStats(wordID int, correct bool) error {
	var query string
	if correct {
		query = "UPDATE words SET correct_count = correct_count + 1 WHERE id = ?"
	} else {
		query = "UPDATE words SET wrong_count = wrong_count + 1 WHERE id = ?"
	}
	
	_, err := s.db.Exec(query, wordID)
	return err
}

// RecordStudyActivity records a study activity for a word
func (s *StudyActivityService) RecordStudyActivity(wordID int, sessionID int, correct bool) error {
	query := `
		INSERT INTO study_activities (word_id, session_id, correct)
		VALUES (?, ?, ?)
	`
	
	_, err := s.db.Exec(query, wordID, sessionID, correct)
	return err
}

// ResetHistory deletes all study sessions and activities but keeps the words and groups
func (s *StudyActivityService) ResetHistory() error {
	tx, err := s.db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()
	
	// Delete all study activities
	if _, err := tx.Exec("DELETE FROM study_activities"); err != nil {
		return err
	}
	
	// Delete all study sessions
	if _, err := tx.Exec("DELETE FROM study_sessions"); err != nil {
		return err
	}
	
	// Reset word counters
	if _, err := tx.Exec("UPDATE words SET correct_count = 0, wrong_count = 0"); err != nil {
		return err
	}
	
	return tx.Commit()
}

// FullReset drops all tables and recreates them with seed data
func (s *StudyActivityService) FullReset() error {
	// In a real app, this would drop all tables and recreate them with seed data
	// For this demo, we'll just delete all data and reset counters
	
	tx, err := s.db.Begin()
	if err != nil {
		return err
	}
	defer tx.Rollback()
	
	// Delete all study activities
	if _, err := tx.Exec("DELETE FROM study_activities"); err != nil {
		return err
	}
	
	// Delete all study sessions
	if _, err := tx.Exec("DELETE FROM study_sessions"); err != nil {
		return err
	}
	
	// Reset word counters
	if _, err := tx.Exec("UPDATE words SET correct_count = 0, wrong_count = 0"); err != nil {
		return err
	}
	
	// Delete word-group associations
	if _, err := tx.Exec("DELETE FROM word_groups"); err != nil {
		return err
	}
	
	// Delete all words
	if _, err := tx.Exec("DELETE FROM words"); err != nil {
		return err
	}
	
	// Delete all groups
	if _, err := tx.Exec("DELETE FROM groups"); err != nil {
		return err
	}
	
	return tx.Commit()
}

// CreateStudySession creates a new study session for the given group and activity
func CreateStudySession(groupID, activityID int) (*models.StudySession, error) {
	// Initialize with zero score/total since the session is just starting
	session := &models.StudySession{
		GroupID:    groupID,
		ActivityID: activityID,
		Score:      0,
		Total:      0,
		CreatedAt:  time.Now(),
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