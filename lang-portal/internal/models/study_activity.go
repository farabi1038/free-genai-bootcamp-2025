package models

import (
	"database/sql"
)

// StudyActivity represents a learning activity
type StudyActivity struct {
	ID           int    `json:"id"`
	Name         string `json:"name"`
	ThumbnailURL string `json:"thumbnail_url"`
	Description  string `json:"description"`
}

// GetActivityByID retrieves a single study activity by its ID
func GetActivityByID(db *sql.DB, id int) (*StudyActivity, error) {
	query := `SELECT id, name, thumbnail_url, description FROM study_activities WHERE id = ?`
	var activity StudyActivity
	err := db.QueryRow(query, id).Scan(
		&activity.ID,
		&activity.Name,
		&activity.ThumbnailURL,
		&activity.Description,
	)
	if err != nil {
		return nil, err
	}
	
	return &activity, nil
}

// GetAllActivities retrieves all study activities
func GetAllActivities(db *sql.DB) ([]StudyActivity, error) {
	query := `SELECT id, name, thumbnail_url, description FROM study_activities`
	rows, err := db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var activities []StudyActivity
	for rows.Next() {
		var activity StudyActivity
		if err := rows.Scan(
			&activity.ID,
			&activity.Name,
			&activity.ThumbnailURL,
			&activity.Description,
		); err != nil {
			return nil, err
		}
		activities = append(activities, activity)
	}

	return activities, nil
} 