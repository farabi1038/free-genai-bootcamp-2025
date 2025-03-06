package models

import (
	"database/sql"
	"time"
	
	_ "github.com/mattn/go-sqlite3"
)

// Word represents a vocabulary word
type Word struct {
	ID           int       `json:"id"`
	Japanese     string    `json:"japanese"`
	Romaji       string    `json:"romaji"`
	English      string    `json:"english"`
	CorrectCount int       `json:"correct_count"`
	WrongCount   int       `json:"wrong_count"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
	Groups       []string  `json:"groups,omitempty"`
}

// WordWithGroups represents a word with its associated groups
type WordWithGroups struct {
	Word
	Groups []Group `json:"groups"`
}

// Group represents a collection of words
type Group struct {
	ID        int       `json:"id"`
	Name      string    `json:"name"`
	WordCount int       `json:"word_count,omitempty"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// GroupWithWords represents a group with its associated words
type GroupWithWords struct {
	Group
	Words []Word `json:"words"`
}

// StudyActivity represents a study activity type
type StudyActivity struct {
	ID           int       `json:"id"`
	Name         string    `json:"name"`
	Description  string    `json:"description"`
	ThumbnailURL string    `json:"thumbnail_url"`
	URL          string    `json:"url"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

// StudySession represents a study session
type StudySession struct {
	ID         int       `json:"id"`
	GroupID    int       `json:"group_id"`
	ActivityID int       `json:"activity_id"`
	Score      int       `json:"score"`
	Total      int       `json:"total"`
	CreatedAt  time.Time `json:"created_at"`
	GroupName  string    `json:"group_name,omitempty"`
}

// StudySessionResponse represents a study session with additional details
type StudySessionResponse struct {
	ID           int       `json:"id"`
	GroupID      int       `json:"group_id"`
	GroupName    string    `json:"group_name"`
	ActivityID   int       `json:"activity_id"`
	ActivityName string    `json:"activity_name"`
	Score        int       `json:"score"`
	Total        int       `json:"total"`
	CreatedAt    time.Time `json:"created_at"`
}

// StudyRecord represents a record of studying a specific word
type StudyRecord struct {
	ID        int       `json:"id"`
	WordID    int       `json:"word_id"`
	SessionID int       `json:"session_id"`
	Correct   bool      `json:"correct"`
	CreatedAt time.Time `json:"created_at"`
}

// StudyRecordWithWord represents a study record with word details
type StudyRecordWithWord struct {
	ID        int       `json:"id"`
	WordID    int       `json:"word_id"`
	Japanese  string    `json:"japanese"`
	Romaji    string    `json:"romaji"`
	English   string    `json:"english"`
	Correct   bool      `json:"correct"`
	CreatedAt time.Time `json:"created_at"`
}

// LastStudySession represents the most recent study session
type LastStudySession struct {
	ID        int       `json:"id"`
	GroupID   int       `json:"group_id"`
	GroupName string    `json:"group_name"`
	Date      time.Time `json:"date"`
	Score     int       `json:"score"`
	Total     int       `json:"total"`
}

// StudyProgress represents the user's study progress
type StudyProgress struct {
	TotalWords    int `json:"total_words"`
	WordsStudied  int `json:"words_studied"`
	WordsMastered int `json:"words_mastered"`
	CompletionRate int `json:"completion_rate"`
}

// QuickStats represents quick statistics for the dashboard
type QuickStats struct {
	TotalGroups   int `json:"total_groups"`
	TotalWords    int `json:"total_words"`
	TotalSessions int `json:"total_sessions"`
	AverageScore  int `json:"average_score"`
}

// createSchema creates the database schema if it doesn't exist
func createSchema(db *sql.DB) error {
	// Create words table
	_, err := db.Exec(`
		CREATE TABLE IF NOT EXISTS words (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			japanese TEXT NOT NULL,
			romaji TEXT NOT NULL,
			english TEXT NOT NULL,
			correct_count INTEGER DEFAULT 0,
			wrong_count INTEGER DEFAULT 0,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
	`)
	if err != nil {
		return err
	}
	
	// Create groups table
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS groups (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
	`)
	if err != nil {
		return err
	}
	
	// Create group_words table (join table)
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS group_words (
			group_id INTEGER,
			word_id INTEGER,
			PRIMARY KEY (group_id, word_id),
			FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
			FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
		)
	`)
	if err != nil {
		return err
	}
	
	// Create study_activities table
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS study_activities (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL,
			description TEXT NOT NULL,
			thumbnail_url TEXT NOT NULL,
			url TEXT NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
	`)
	if err != nil {
		return err
	}
	
	// Create study_sessions table
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS study_sessions (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			group_id INTEGER NOT NULL,
			activity_id INTEGER NOT NULL,
			score INTEGER DEFAULT 0,
			total INTEGER DEFAULT 0,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
			FOREIGN KEY (activity_id) REFERENCES study_activities(id) ON DELETE CASCADE
		)
	`)
	if err != nil {
		return err
	}
	
	// Create study_records table
	_, err = db.Exec(`
		CREATE TABLE IF NOT EXISTS study_records (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			word_id INTEGER NOT NULL,
			session_id INTEGER NOT NULL,
			correct BOOLEAN NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE,
			FOREIGN KEY (session_id) REFERENCES study_sessions(id) ON DELETE CASCADE
		)
	`)
	if err != nil {
		return err
	}
	
	// Insert default data if tables are empty
	return insertDefaultData(db)
}

// insertDefaultData inserts default data if tables are empty
func insertDefaultData(db *sql.DB) error {
	// Check if the study_activities table is empty
	var count int
	err := db.QueryRow("SELECT COUNT(*) FROM study_activities").Scan(&count)
	if err != nil {
		return err
	}
	
	// If no activities exist, insert default ones
	if count == 0 {
		activities := []struct {
			name        string
			description string
			thumbnail   string
			url         string
		}{
			{
				name:        "Flashcards",
				description: "Traditional flashcard study with Japanese on one side and English on the other",
				thumbnail:   "/assets/thumbnails/flashcards.png",
				url:         "/study/flashcards",
			},
			{
				name:        "Multiple Choice",
				description: "Test your knowledge with multiple choice questions",
				thumbnail:   "/assets/thumbnails/multiple-choice.png",
				url:         "/study/multiple-choice",
			},
			{
				name:        "Typing Practice",
				description: "Improve your typing skills by writing out the Japanese or English translations",
				thumbnail:   "/assets/thumbnails/typing.png",
				url:         "/study/typing",
			},
			{
				name:        "Matching Game",
				description: "Match Japanese words with their English translations in a memory-style game",
				thumbnail:   "/assets/thumbnails/matching.png",
				url:         "/study/matching",
			},
		}
		
		for _, activity := range activities {
			_, err := db.Exec(
				"INSERT INTO study_activities (name, description, thumbnail_url, url) VALUES (?, ?, ?, ?)",
				activity.name, activity.description, activity.thumbnail, activity.url,
			)
			if err != nil {
				return err
			}
		}
	}
	
	// Check if groups table is empty
	err = db.QueryRow("SELECT COUNT(*) FROM groups").Scan(&count)
	if err != nil {
		return err
	}
	
	// If no groups exist, insert default ones
	if count == 0 {
		groups := []string{
			"Common Greetings",
			"Basic Conversation",
			"Numbers and Counting",
			"Food and Dining",
			"Travel Phrases",
		}
		
		for _, group := range groups {
			_, err := db.Exec("INSERT INTO groups (name) VALUES (?)", group)
			if err != nil {
				return err
			}
		}
	}
	
	// Check if words table is empty
	err = db.QueryRow("SELECT COUNT(*) FROM words").Scan(&count)
	if err != nil {
		return err
	}
	
	// If no words exist, insert default ones
	if count == 0 {
		words := []struct {
			japanese string
			romaji   string
			english  string
			groupID  int
		}{
			{
				japanese: "こんにちは",
				romaji:   "konnichiwa",
				english:  "hello",
				groupID:  1,
			},
			{
				japanese: "さようなら",
				romaji:   "sayounara",
				english:  "goodbye",
				groupID:  1,
			},
			{
				japanese: "ありがとう",
				romaji:   "arigatou",
				english:  "thank you",
				groupID:  1,
			},
			{
				japanese: "はい",
				romaji:   "hai",
				english:  "yes",
				groupID:  2,
			},
			{
				japanese: "いいえ",
				romaji:   "iie",
				english:  "no",
				groupID:  2,
			},
			{
				japanese: "お願いします",
				romaji:   "onegaishimasu",
				english:  "please",
				groupID:  2,
			},
			{
				japanese: "一",
				romaji:   "ichi",
				english:  "one",
				groupID:  3,
			},
			{
				japanese: "二",
				romaji:   "ni",
				english:  "two",
				groupID:  3,
			},
			{
				japanese: "三",
				romaji:   "san",
				english:  "three",
				groupID:  3,
			},
			{
				japanese: "ご飯",
				romaji:   "gohan",
				english:  "rice/meal",
				groupID:  4,
			},
			{
				japanese: "水",
				romaji:   "mizu",
				english:  "water",
				groupID:  4,
			},
			{
				japanese: "お茶",
				romaji:   "ocha",
				english:  "tea",
				groupID:  4,
			},
			{
				japanese: "駅",
				romaji:   "eki",
				english:  "station",
				groupID:  5,
			},
			{
				japanese: "電車",
				romaji:   "densha",
				english:  "train",
				groupID:  5,
			},
			{
				japanese: "バス",
				romaji:   "basu",
				english:  "bus",
				groupID:  5,
			},
		}
		
		for _, word := range words {
			// Insert word
			result, err := db.Exec(
				"INSERT INTO words (japanese, romaji, english) VALUES (?, ?, ?)",
				word.japanese, word.romaji, word.english,
			)
			if err != nil {
				return err
			}
			
			// Get the inserted word ID
			wordID, err := result.LastInsertId()
			if err != nil {
				return err
			}
			
			// Associate with group
			_, err = db.Exec(
				"INSERT INTO group_words (group_id, word_id) VALUES (?, ?)",
				word.groupID, wordID,
			)
			if err != nil {
				return err
			}
		}
	}
	
	return nil
} 