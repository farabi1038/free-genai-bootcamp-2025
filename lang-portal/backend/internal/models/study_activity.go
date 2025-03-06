package models

import (
	"database/sql"
	"time"
)

// GetActivityByID retrieves a single study activity by its ID
func GetActivityByID(db *sql.DB, id int) (*StudyActivity, error) {
	query := `SELECT id, name, description, thumbnail_url, url, created_at, updated_at FROM study_activities WHERE id = ?`
	var activity StudyActivity
	var createdAt, updatedAt string
	
	err := db.QueryRow(query, id).Scan(
		&activity.ID,
		&activity.Name,
		&activity.Description,
		&activity.ThumbnailURL,
		&activity.URL,
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
	activity.CreatedAt, _ = time.Parse("2006-01-02 15:04:05", createdAt)
	activity.UpdatedAt, _ = time.Parse("2006-01-02 15:04:05", updatedAt)
	
	return &activity, nil
}

// GetAllActivities retrieves all available study activities
func GetAllActivities(db *sql.DB) ([]StudyActivity, error) {
	query := `SELECT id, name, description, thumbnail_url, url, created_at, updated_at FROM study_activities`
	rows, err := db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	var activities []StudyActivity
	for rows.Next() {
		var activity StudyActivity
		var createdAt, updatedAt string
		
		err := rows.Scan(
			&activity.ID,
			&activity.Name,
			&activity.Description,
			&activity.ThumbnailURL,
			&activity.URL,
			&createdAt,
			&updatedAt,
		)
		
		if err != nil {
			return nil, err
		}
		
		// Parse timestamps
		activity.CreatedAt, _ = time.Parse("2006-01-02 15:04:05", createdAt)
		activity.UpdatedAt, _ = time.Parse("2006-01-02 15:04:05", updatedAt)
		
		activities = append(activities, activity)
	}
	
	if err = rows.Err(); err != nil {
		return nil, err
	}
	
	return activities, nil
} 