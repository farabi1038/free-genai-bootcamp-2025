package models

import (
	"database/sql"
	"fmt"
)

// TestDB holds a reference to the test database
type TestDB struct {
	DB *sql.DB
}

// TestData represents the data to be seeded into the test database
type TestData struct {
	Words      []Word
	Groups     []Group
	Activities []StudyActivity
}

// SeedTestData seeds the test database with the provided test data
func SeedTestData(db *sql.DB, data TestData) (*TestDB, error) {
	// Insert test words
	for _, word := range data.Words {
		_, err := db.Exec(
			"INSERT INTO words (japanese, romaji, english) VALUES (?, ?, ?)",
			word.Japanese, word.Romaji, word.English,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to insert test word: %v", err)
		}
	}

	// Insert test groups
	for _, group := range data.Groups {
		_, err := db.Exec(
			"INSERT INTO groups (name) VALUES (?)",
			group.Name,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to insert test group: %v", err)
		}
	}

	// Insert test words_groups associations
	// For simplicity, associate first word with first group, second word with second group
	for i := 0; i < len(data.Words) && i < len(data.Groups); i++ {
		_, err := db.Exec(
			"INSERT INTO words_groups (group_id, word_id) VALUES (?, ?)",
			i+1, i+1,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to insert test words_group: %v", err)
		}
	}

	// Insert test study activities
	for _, activity := range data.Activities {
		_, err := db.Exec(
			"INSERT INTO study_activities (name, thumbnail_url, description) VALUES (?, ?, ?)",
			activity.Name, activity.ThumbnailURL, activity.Description,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to insert test activity: %v", err)
		}
	}

	return &TestDB{DB: db}, nil
} 