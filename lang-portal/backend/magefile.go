// +build mage

package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"

	_ "github.com/mattn/go-sqlite3"
)

// Word represents a vocabulary word for seeding
type Word struct {
	Japanese string          `json:"japanese"`
	Romaji   string          `json:"romaji"`
	English  string          `json:"english"`
	Parts    json.RawMessage `json:"parts,omitempty"`
}

// Group represents a word group for seeding
type Group struct {
	Name string `json:"name"`
}

// StudyActivity represents a study activity for seeding
type StudyActivity struct {
	Name         string `json:"name"`
	ThumbnailURL string `json:"thumbnail_url"`
	Description  string `json:"description"`
}

const dbFile = "words.db"

// InitDB initializes the SQLite database file
func InitDB() error {
	fmt.Println("Initializing database...")
	
	if _, err := os.Stat(dbFile); os.IsNotExist(err) {
		fmt.Println("Creating database file:", dbFile)
		file, err := os.Create(dbFile)
		if err != nil {
			return fmt.Errorf("failed to create database file: %v", err)
		}
		file.Close()
	} else {
		fmt.Println("Database file already exists, skipping creation")
	}
	
	return nil
}

// MigrateDB runs database migrations
func MigrateDB() error {
	fmt.Println("Running database migrations...")
	
	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		return fmt.Errorf("failed to open database: %v", err)
	}
	defer db.Close()
	
	migrationsDir := "db/migrations"
	migrations, err := filepath.Glob(filepath.Join(migrationsDir, "*.sql"))
	if err != nil {
		return fmt.Errorf("failed to find migration files: %v", err)
	}
	
	for _, migration := range migrations {
		fmt.Println("Applying migration:", migration)
		migrationData, err := ioutil.ReadFile(migration)
		if err != nil {
			return fmt.Errorf("failed to read migration file: %v", err)
		}
		
		_, err = db.Exec(string(migrationData))
		if err != nil {
			return fmt.Errorf("failed to apply migration: %v", err)
		}
	}
	
	return nil
}

// SeedDB imports seed data into the database
func SeedDB() error {
	fmt.Println("Seeding database with initial data...")
	
	db, err := sql.Open("sqlite3", dbFile)
	if err != nil {
		return fmt.Errorf("failed to open database: %v", err)
	}
	defer db.Close()
	
	// Seed words
	words, err := loadWords("db/seeds/01_words.json")
	if err != nil {
		return err
	}
	
	for _, word := range words {
		fmt.Printf("Inserting word: %s\n", word.Japanese)
		_, err = db.Exec(
			"INSERT INTO words (japanese, romaji, english, parts) VALUES (?, ?, ?, ?)",
			word.Japanese, word.Romaji, word.English, word.Parts,
		)
		if err != nil {
			return fmt.Errorf("failed to insert word: %v", err)
		}
	}
	
	// Seed groups
	groups, err := loadGroups("db/seeds/02_groups.json")
	if err != nil {
		return err
	}
	
	for _, group := range groups {
		fmt.Printf("Inserting group: %s\n", group.Name)
		_, err = db.Exec("INSERT INTO groups (name) VALUES (?)", group.Name)
		if err != nil {
			return fmt.Errorf("failed to insert group: %v", err)
		}
	}
	
	// Seed study activities
	activities, err := loadActivities("db/seeds/03_study_activities.json")
	if err != nil {
		return err
	}
	
	for _, activity := range activities {
		fmt.Printf("Inserting activity: %s\n", activity.Name)
		_, err = db.Exec(
			"INSERT INTO study_activities (name, thumbnail_url, description) VALUES (?, ?, ?)",
			activity.Name, activity.ThumbnailURL, activity.Description,
		)
		if err != nil {
			return fmt.Errorf("failed to insert activity: %v", err)
		}
	}
	
	// Assign words to groups based on their content
	// Basic Greetings: hello, goodbye, good morning, good evening, good night
	greetingWords := []string{"hello", "goodbye", "good morning", "good evening", "good night"}
	err = assignWordsToGroup(db, greetingWords, "Basic Greetings")
	if err != nil {
		return err
	}
	
	// Common Phrases: thank you, excuse me, yes, no
	commonPhrases := []string{"thank you", "excuse me", "yes", "no"}
	err = assignWordsToGroup(db, commonPhrases, "Common Phrases")
	if err != nil {
		return err
	}
	
	// All words go into Daily Conversations
	allWords := []string{"hello", "goodbye", "thank you", "excuse me", "yes", "no", "good morning", "good evening", "good night", "I"}
	err = assignWordsToGroup(db, allWords, "Daily Conversations")
	if err != nil {
		return err
	}
	
	return nil
}

// loadWords loads word data from a JSON file
func loadWords(filePath string) ([]Word, error) {
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read words seed file: %v", err)
	}
	
	var words []Word
	err = json.Unmarshal(data, &words)
	if err != nil {
		return nil, fmt.Errorf("failed to parse words seed data: %v", err)
	}
	
	return words, nil
}

// loadGroups loads group data from a JSON file
func loadGroups(filePath string) ([]Group, error) {
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read groups seed file: %v", err)
	}
	
	var groups []Group
	err = json.Unmarshal(data, &groups)
	if err != nil {
		return nil, fmt.Errorf("failed to parse groups seed data: %v", err)
	}
	
	return groups, nil
}

// loadActivities loads activity data from a JSON file
func loadActivities(filePath string) ([]StudyActivity, error) {
	data, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, fmt.Errorf("failed to read activities seed file: %v", err)
	}
	
	var activities []StudyActivity
	err = json.Unmarshal(data, &activities)
	if err != nil {
		return nil, fmt.Errorf("failed to parse activities seed data: %v", err)
	}
	
	return activities, nil
}

// assignWordsToGroup assigns words to a group based on their English translation
func assignWordsToGroup(db *sql.DB, englishWords []string, groupName string) error {
	var groupID int
	err := db.QueryRow("SELECT id FROM groups WHERE name = ?", groupName).Scan(&groupID)
	if err != nil {
		return fmt.Errorf("failed to find group '%s': %v", groupName, err)
	}
	
	for _, english := range englishWords {
		var wordID int
		err := db.QueryRow("SELECT id FROM words WHERE english = ?", english).Scan(&wordID)
		if err != nil {
			fmt.Printf("Warning: word '%s' not found, skipping\n", english)
			continue
		}
		
		_, err = db.Exec("INSERT INTO words_groups (word_id, group_id) VALUES (?, ?)", wordID, groupID)
		if err != nil {
			return fmt.Errorf("failed to assign word to group: %v", err)
		}
	}
	
	return nil
}

// SetupDB runs the complete database setup process
func SetupDB() {
	fmt.Println("Setting up database...")
	
	err := InitDB()
	if err != nil {
		fmt.Printf("Error initializing database: %v\n", err)
		return
	}
	
	err = MigrateDB()
	if err != nil {
		fmt.Printf("Error running migrations: %v\n", err)
		return
	}
	
	err = SeedDB()
	if err != nil {
		fmt.Printf("Error seeding database: %v\n", err)
		return
	}
	
	fmt.Println("Database setup complete!")
} 